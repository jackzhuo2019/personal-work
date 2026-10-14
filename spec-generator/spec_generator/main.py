"""Main orchestrator — runs the 5-step spec generation pipeline."""
import argparse
import json
import logging
import os
import sys
import webbrowser
from datetime import datetime
from pathlib import Path

from .config import load_settings, SpecResult
from .agents.llm_helper import LLMHelper
from .agents.requirement_agent import RequirementAgent
from .agents.data_model_agent import DataModelAgent
from .agents.state_machine_agent import StateMachineAgent
from .agents.test_case_agent import TestCaseAgent
from .agents.prototype_agent import PrototypeAgent
from .agents.review_agent import ReviewAgent
from .prd_generator import generate_prd
from .svg_generator import generate_state_machine_svg

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("spec_generator")


def generate_spec(business_description: str, config_path: str | None = None) -> SpecResult:
    """Run the full spec generation pipeline.

    Pipeline:
    1. Requirement Agent → requirements, user roles, use cases
    2. Data Model Agent → entities, fields, validation
    3. State Machine Agent → state transitions
    4. Test Case Agent → test cases
    5. Prototype Agent → interactive HTML
    6. Review Agent → adversarial review
    7. Generate PRD Markdown + SVG
    """
    logger.info("=" * 60)
    logger.info("Starting Product Spec Generation")
    logger.info(f"Input: {business_description[:80]}...")
    logger.info("=" * 60)

    settings = load_settings(config_path)
    llm = LLMHelper(settings.llm.base_url, settings.llm.api_key, settings.llm.model)

    result = SpecResult(business_description=business_description)

    # Step 1: Requirements
    logger.info("Step 1/6: Requirement Agent...")
    req_agent = RequirementAgent(llm)
    requirements = req_agent.run(business_description)
    result.requirements = requirements.get("requirements", [])
    result.user_roles = requirements.get("user_roles", [])

    # Step 2: Data Model
    logger.info("Step 2/6: Data Model Agent...")
    dm_agent = DataModelAgent(llm)
    data_models = dm_agent.run(business_description, requirements)
    result.data_models = data_models.get("models", [])

    # Step 3: State Machine
    logger.info("Step 3/6: State Machine Agent...")
    sm_agent = StateMachineAgent(llm)
    state_machines = sm_agent.run(business_description, data_models)
    result.state_machines = state_machines.get("state_machines", [])

    # Step 4: Test Cases
    logger.info("Step 4/6: Test Case Agent...")
    tc_agent = TestCaseAgent(llm)
    test_cases = tc_agent.run(business_description, requirements, data_models, state_machines)
    result.test_cases = test_cases.get("test_cases", [])

    # Step 5: Prototype
    logger.info("Step 5/6: Prototype Agent...")
    proto_agent = PrototypeAgent(llm)
    result.prototype_html = proto_agent.run(business_description, requirements, data_models, state_machines)

    # Step 6: Review
    logger.info("Step 6/6: Review Agent...")
    review_agent = ReviewAgent(llm)
    review = review_agent.run(business_description, requirements, data_models, state_machines, test_cases)
    result.review_notes = review.get("overall_assessment", "")

    # Generate outputs
    logger.info("Generating outputs...")

    result.prd_markdown = generate_prd(
        business_description, requirements, data_models, state_machines, test_cases, review
    )

    result.state_machine_svg = generate_state_machine_svg(result.state_machines)

    # Save to files
    output_dir = Path(settings.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    prd_path = output_dir / f"prd_{timestamp}.md"
    prd_path.write_text(result.prd_markdown, encoding="utf-8")

    proto_path = output_dir / f"prototype_{timestamp}.html"
    proto_path.write_text(result.prototype_html, encoding="utf-8")

    svg_path = output_dir / f"state_machine_{timestamp}.svg"
    svg_path.write_text(result.state_machine_svg, encoding="utf-8")

    # Save full JSON
    json_path = output_dir / f"spec_{timestamp}.json"
    full_json = {
        "business_description": business_description,
        "requirements": requirements,
        "data_models": data_models,
        "state_machines": state_machines,
        "test_cases": test_cases,
        "review": review,
        "generated_at": datetime.now().isoformat(),
    }
    json_path.write_text(json.dumps(full_json, ensure_ascii=False, indent=2), encoding="utf-8")

    logger.info("=" * 60)
    logger.info(f"Spec generation complete!")
    logger.info(f"  PRD:         {prd_path}")
    logger.info(f"  Prototype:   {proto_path}")
    logger.info(f"  State Machine SVG: {svg_path}")
    logger.info(f"  Full JSON:   {json_path}")
    logger.info(f"  Review: {result.review_notes}")
    logger.info("=" * 60)

    result.output_files = {
        "prd": str(prd_path),
        "prototype": str(proto_path),
        "state_machine": str(svg_path),
        "json": str(json_path),
    }

    return result


def main():
    parser = argparse.ArgumentParser(description="Product Spec Generator")
    parser.add_argument("description", nargs="?", help="Business description (or use --interactive)")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode")
    parser.add_argument("--config", default=None, help="Path to settings.yaml")
    parser.add_argument("--open", action="store_true", help="Open prototype in browser after generation")

    args = parser.parse_args()

    if args.interactive or not args.description:
        print("Enter business description (Ctrl+D to submit):")
        lines = []
        try:
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            pass
        description = "\n".join(lines).strip()
        if not description:
            print("No description provided.")
            sys.exit(1)
    else:
        description = args.description

    result = generate_spec(description, args.config)

    if args.open and result.output_files.get("prototype"):
        webbrowser.open(f"file://{os.path.abspath(result.output_files['prototype'])}")


if __name__ == "__main__":
    main()