import argparse
import traceback
import re
import json
import asyncio
from rich.console import Console
from rich.panel import Panel
from dotenv import load_dotenv
from agents import Agent, Runner, ItemHelpers

console = Console()
load_dotenv(".env", override=True)


def clean_filename(text):
    cleaned = re.sub(r"[^\w\s-]", "", text.lower())
    cleaned = re.sub(r"[-\s]+", "_", cleaned)
    return cleaned[:50]


async def generate_prompt_async(requirement: str, verbose: bool = True) -> str:
    """
    Async function to generate a prompt with streaming capabilities
    """
    try:
        if verbose:
            console.print(Panel(f"[bold blue]Generating prompt for:[/]\n{requirement}"))

        prompt_generator_agent = Agent(
            name="PromptGeneratorAgent",
            instructions="Generate a prompt based on the requirement.",
            model="gpt-4.1",
        )
        prompt_reviewer_agent = Agent(
            name="PromptReviewerAgent",
            instructions="Review the generated prompt for quality and relevance.",
            model="gpt-4.1",
        )
        refine_prompt_agent = Agent(
            name="PromptRefineAgent",
            instructions="Refine the generated prompt based on feedback.",
            model="gpt-4.1",
        )
        prompt_expander_agent = Agent(
            name="PromptExpanderAgent",
            instructions="Expand the generated prompt with additional details.",
            model="gpt-4.1",
        )

        orchestrator = Agent(
            name="PromptOrchestrator",
            instructions=f"""
            Orchestrate the prompt generation, review, and refinement process. 
            Expand the prompt with additional details and ensure it meets the requirement.

            1. Use the PromptGeneratorAgent to create an initial prompt based on the requirement.
            2. Use the PromptReviewerAgent to review the generated prompt for quality and relevance.
            3. Use the PromptRefineAgent to refine the generated prompt based on feedback.
            4. Use the PromptExpanderAgent to expand the generated prompt with additional details.
            5. If the prompt is not satisfactory, repeat the process with the refined prompt. 
            6. To check if the prompt is satisfactory, use the PromptReviewerAgent to evaluate the prompt.
            7. If the prompt is satisfactory, finalize it and return the result.

            Repeat the process until the prompt is satisfactory.
            """,
            model="gpt-4.1",
            tools=[
                prompt_generator_agent.as_tool(
                    tool_name="PromptGenerator",
                    tool_description="Generate a prompt based on the requirement.",
                ),
                prompt_reviewer_agent.as_tool(
                    tool_name="PromptReviewer",
                    tool_description="Review the generated prompt for quality and relevance.",
                ),
                refine_prompt_agent.as_tool(
                    tool_name="PromptRefine",
                    tool_description="Refine the generated prompt based on feedback.",
                ),
                prompt_expander_agent.as_tool(
                    tool_name="PromptExpander",
                    tool_description="Expand the generated prompt with additional details.",
                ),
            ],
        )

        result = Runner.run_streamed(
            orchestrator,
            input=f"Generate a prompt for the following requirement: {requirement}",
            max_turns=30,
        )

        final_output = None
        async for event in result.stream_events():
            if event.type == "agent_updated_stream_event" and verbose:
                console.print(f"[blue]Agent active:[/] {event.new_agent.name}")
            elif event.type == "run_item_stream_event":
                if event.item.type == "tool_call_item" and verbose:
                    console.print(
                        f"[yellow]Calling tool:[/] {event.item.raw_item.model_dump_json(indent=4)}"
                    )
                elif event.item.type == "message_output_item":
                    final_output = ItemHelpers.text_message_output(event.item)
                    if verbose:
                        console.print("[green]Generated output...[/]")

        if verbose:
            console.print("[green]✓[/] Prompt generation complete!")

        return final_output

    except Exception as e:
        console.print(f"[red]Error generating prompt: {e}[/]")
        if verbose:
            console.print(
                Panel(traceback.format_exc(), title="[red]Exception Details[/]")
            )
        return f"Error generating prompt for requirement: {requirement}. Exception: {str(e)}"


def generate_prompt(requirement: str, verbose: bool = True) -> str:
    """
    Synchronous wrapper for the async prompt generation
    """
    return asyncio.run(generate_prompt_async(requirement, verbose))


def save_prompt(prompt, output_file, verbose: bool = True):
    """
    Save the generated prompt to a file
    """
    with open(output_file, "w") as f:
        f.write(prompt)
    if verbose:
        console.print(f"[green]✓[/] Saved prompt to: {output_file}")


def process_batch(requirements, verbose: bool = True):
    """
    Process a list of requirements and generate prompts for each
    Returns a dictionary of requirement: prompt pairs
    """
    results = {}
    for req in requirements:
        if verbose:
            console.print(f"[blue]Processing requirement:[/] {req}")
        results[req] = generate_prompt(req, verbose)
    return results


def main():
    parser = argparse.ArgumentParser(description="Generate prompts from requirements")
    parser.add_argument("--req", help="The requirement to generate a prompt for")
    parser.add_argument("--output", help="Output file path (optional)")
    parser.add_argument(
        "-i", "--input", help="JSON file containing list of requirements"
    )
    parser.add_argument(
        "--no-verbose", action="store_true", help="Disable verbose output"
    )

    args = parser.parse_args()
    verbose = not args.no_verbose

    if not args.req and not args.input:
        parser.error("Either --req or -i must be provided")

    if args.req and args.input:
        parser.error("Cannot use both --req and -i together")

    if args.input:
        with open(args.input, "r") as f:
            requirements = json.load(f)

        if not isinstance(requirements, list):
            raise ValueError("JSON file must contain a list of requirements")

        results = process_batch(requirements, verbose)
        output_file = args.output or "batch_prompts.md"

        with open(output_file, "w") as f:
            for req, prompt in results.items():
                f.write(f"### Requirement: {req}\n\n{prompt}\n\n---\n\n")

        if verbose:
            console.print(f"[green]✓[/] Batch prompts saved to: {output_file}")
    else:
        prompt = generate_prompt(args.req, verbose)
        if args.output:
            output_file = args.output
        else:
            filename = clean_filename(args.req) + ".md"
            output_file = filename

        save_prompt(prompt, output_file, verbose)


if __name__ == "__main__":
    main()
