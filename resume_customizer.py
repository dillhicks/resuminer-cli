#!/usr/bin/env python3
"""
Resume Customizer CLI Tool

A CLI tool that uses OpenRouter and GPT-5 to customize resumes based on job postings.
Takes a job posting (txt file) and resume (renderCV YAML) and modifies the resume
to better match the job requirements by reordering experience highlights and updating
technologies sections.
"""

import os
import sys
import json
import tempfile
import subprocess
from pathlib import Path

import click
import yaml
from dotenv import load_dotenv
from openai import OpenAI

# Optional desktop notification support
# Install plyer with: pip install plyer
try:
    from plyer import notification
except ImportError:
    notification = None

# Load environment variables from .env file
load_dotenv()


class ResumeCustomizer:
    """Main class for customizing resumes based on job postings."""

    def __init__(self, api_key: str):
        """Initialize with OpenRouter API key."""
        self.api_key = api_key
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )

    def read_file(self, file_path: str) -> str:
        """Read file content as string."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise click.ClickException(f"Error reading {file_path}: {str(e)}")

    def call_openrouter(self, resume_content: str, job_posting: str) -> str:
        """Call OpenRouter API with GPT-5 to customize resume."""
        prompt = self._create_prompt(resume_content, job_posting)

        # Clean the response by removing markdown formatting
        response_content = self._make_api_call(prompt)

        # Remove markdown code block formatting if present
        cleaned_content = self._clean_yaml_response(response_content)

        return cleaned_content

    def _make_api_call(self, prompt: str) -> str:
        """Make the actual API call to OpenRouter using OpenAI client."""
        try:
            # Create the full prompt with system message included
            full_prompt = "You are an expert resume writer and ATS optimization specialist. You will receive a resume in YAML format and a job posting. Your task is to modify ONLY the highlights in the Experience section and the Technologies section to better match the job posting while keeping all other content exactly the same.\n\n" + prompt

            completion = self.client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": "https://github.com/    -repo/resume-customizer",
                    "X-Title": "Resume Customizer CLI",
                },
                model="openai/gpt-5-mini",  

                messages=[
                    {
                        "role": "user",
                        "content": full_prompt
                    }
                ],
                temperature=0.2,  # Medium reasoning effort - between focused (0.1) and creative (0.3)
            )

            return completion.choices[0].message.content.strip()

        except Exception as e:
            raise click.ClickException(f"API request failed: {str(e)}")

    def _clean_yaml_response(self, response_content: str) -> str:
        """Clean YAML response by removing markdown formatting."""
        # Remove markdown code block markers
        cleaned = response_content.strip()

        # Remove ```yaml or ```yml markers
        if cleaned.startswith('```yaml'):
            cleaned = cleaned[7:].strip()
        elif cleaned.startswith('```yml'):
            cleaned = cleaned[7:].strip()
        elif cleaned.startswith('```'):
            cleaned = cleaned[3:].strip()

        # Remove ending ``` if present
        if cleaned.endswith('```'):
            cleaned = cleaned[:-3].strip()

        return cleaned

    def _create_prompt(self, resume_content: str, job_posting: str) -> str:
        """Create the comprehensive prompt for GPT-5."""
        return f"""
JOB POSTING:
{job_posting}

CURRENT RESUME (YAML format):
{resume_content}

INSTRUCTIONS:
Please modify the resume to better match this job posting. You must:

1. EXPERIENCE SECTION HIGHLIGHTS:
   - Reorder the highlights (bullet points) within each job in the Experience section
   - Put the most relevant highlights first based on the job posting requirements
   - Keep all highlights but reorder them by relevance to the job posting
   - Do not add, remove, or modify the content of highlights - only reorder them

2. TECHNOLOGIES SECTION:
   - Remove technologies that are not relevant at all to the job posting
   - Keep technologies that are mentioned or very closely related to those in the job posting
   - Reorder the technologies to put the most relevant ones first, and reorder each technology category if needed.
   - Add important technologies from the job posting that are missing but would be relevant. 
   - Only add important technologies that are equivalents or very closely related to those already listed in the resume.
   - Only modify the "details" field within each technology category
   - Maintain the same technology categories/labels

3. IMPORTANT RESTRICTIONS:
   - ONLY modify the highlights in the Experience section and details in the Technologies section
   - Keep all other sections, formatting, and content exactly the same
   - Return the complete modified YAML with proper formatting
   - Do not change section names, structure, or any other content

CRITICAL: Return ONLY the raw YAML content. Do not wrap it in code blocks, markdown, or any other formatting. Return the YAML exactly as it should be parsed. Be direct and focused in your modifications.
"""

    def save_temp_resume(self, modified_yaml: str) -> str:
        """Save modified YAML to temporary file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False, encoding='utf-8') as f:
            f.write(modified_yaml)
            return f.name

    def render_resume(self, temp_file: str, output_name: str = "tempresume") -> None:
        """Render resume using renderCV."""
        try:
            # Use rendercv render command
            cmd = ["rendercv", "render", temp_file]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            click.echo(f"Resume rendered successfully as '{output_name}.pdf'")
            click.echo("RenderCV output:", err=True)
            click.echo(result.stderr, err=True)

        except subprocess.CalledProcessError as e:
            raise click.ClickException(f"Failed to render resume: {e.stderr}")
        except FileNotFoundError:
            raise click.ClickException("rendercv command not found. Please ensure renderCV is installed.")
        finally:
            # Keep temporary file for inspection (user requested)
            click.echo(f"Temporary YAML file saved as: {temp_file}")
            click.echo("You can inspect the modified resume YAML file before deleting it.")

    def customize_resume(self, resume_file: str, job_posting_file: str, output_name: str = "tempresume") -> None:
            """Main method to customize resume."""
            # Check for API key in environment
            api_key = os.getenv('OPENROUTER_API_KEY')
            if not api_key:
                raise click.ClickException(
                    "OpenRouter API key not found. Please set OPENROUTER_API_KEY in your .env file.\n"
                    "Example .env file:\nOPENROUTER_API_KEY=sk-or-v1-your-key-here"
                )

            # Update the API key and reinitialize the OpenAI client
            self.api_key = api_key
            self.client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key,
            )
    
            # Read input files
            resume_content = self.read_file(resume_file)
            job_posting = self.read_file(job_posting_file)
    
            # Validate YAML format
            try:
                yaml.safe_load(resume_content)
            except yaml.YAMLError as e:
                raise click.ClickException(f"Invalid YAML format in resume file: {str(e)}")
    
            # Call OpenRouter API
            click.echo("Customizing resume with AI...")
            modified_yaml = self.call_openrouter(resume_content, job_posting)
    
            # Validate modified YAML
            try:
                yaml.safe_load(modified_yaml)
            except yaml.YAMLError as e:
                raise click.ClickException(f"AI returned invalid YAML: {str(e)}")
    
            # Save and render
            temp_file = self.save_temp_resume(modified_yaml)
            self.render_resume(temp_file, output_name)


@click.group()
def cli():
    """Resume Customizer CLI Tool"""
    pass


@cli.command()
@click.argument('resume_file', type=click.Path(exists=True))
@click.argument('job_posting_file', type=click.Path(exists=True))
@click.option('--output', '-o', default='tempresume', help='Output filename (without extension)')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def customize(resume_file, job_posting_file, output, verbose):
    """Customize a resume based on a job posting."""
    try:
        customizer = ResumeCustomizer("")  # API key will be loaded from environment

        if verbose:
            click.echo(f"Processing resume: {resume_file}")
            click.echo(f"Job posting: {job_posting_file}")
            click.echo(f"Output: {output}")

        customizer.customize_resume(resume_file, job_posting_file, output)

        click.echo("✅ Resume customization completed successfully!")

        # Send desktop notification if plyer is available
        if notification:
            try:
                notification.notify(
                    title="Resume Customization Complete",
                    message=f"Resume has been successfully customized and saved as '{output}.pdf'",
                    app_name="Resume Customizer",
                    timeout=5
                )
            except Exception:
                # Silently fail if notification fails - don't interrupt the main flow
                pass

    except click.ClickException as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Unexpected error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli()