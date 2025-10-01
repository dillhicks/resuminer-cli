# Resuminer CLI

Resuminer CLI is a command-line tool that customizes resumes based on job postings using AI. It analyzes job requirements and modifies resume content to better match the target position by reordering experience highlights and updating technology sections.

## Features

- Analyzes job postings to identify key requirements and skills
- Reorders resume highlights to emphasize relevant experience
- Updates technology sections to prioritize job-relevant skills
- Generates customized PDF resumes using renderCV
- Supports multiple resume formats through YAML configuration

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Install renderCV for PDF generation:
```bash
pip install rendercv
```

## Setup

### 1. Environment Configuration

Create a `.env` file in the project root with your OpenRouter API key:

```
OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

Get your API key from [OpenRouter](https://openrouter.ai/).

### 2. Resume Configuration

Prepare your resume in YAML format compatible with renderCV. The tool expects:

- A YAML file containing your resume data
- Standard renderCV structure with Experience and Technologies sections
- Job posting in plain text format

Example resume structure:
```yaml
# Basic Information
name: "Your Name"
position: "Your Position"

# Experience section with highlights
experience:
  - company: "Company Name"
    position: "Position"
    highlights:
      - "Relevant achievement 1"
      - "Relevant achievement 2"

# Technologies section
technologies:
  - category: "Programming Languages"
    details: "Python, JavaScript, Java"
```

### 3. Job Posting

Prepare your target job posting as a plain text file containing the full job description.

## Usage

Basic usage:
```bash
python resume_customizer.py customize resume.yml posting.txt --output customized_resume
```

Command options:
- `resume_file`: Path to your resume YAML file (required)
- `job_posting_file`: Path to the job posting text file (required)
- `--output, -o`: Output filename without extension (default: tempresume)
- `--verbose, -v`: Enable verbose output

Example with verbose output:
```bash
python resume_customizer.py customize my_resume.yml job_posting.txt --output software_engineer_resume --verbose
```

The tool will:
1. Read and validate your resume YAML file
2. Analyze the job posting content
3. Send both to the AI service for customization
4. Generate an updated YAML file
5. Render the final PDF using renderCV

## Output

The tool generates:
- A customized PDF resume (e.g., `software_engineer_resume.pdf`)
- A temporary YAML file for inspection (saved for review before deletion)

## Dependencies

- OpenAI Python client for API communication
- renderCV for PDF generation
- Click for CLI interface
- PyYAML for YAML processing
- python-dotenv for environment variable management
- plyer (optional) for desktop notifications

## Error Handling

The tool includes validation for:
- YAML format correctness
- API key presence
- File accessibility
- renderCV installation

Error messages provide specific guidance for resolving issues.