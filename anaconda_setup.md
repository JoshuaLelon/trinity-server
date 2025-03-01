# Using Anaconda with Trinity Journaling App

This guide explains how to set up and use Anaconda for Trinity Journaling App development and deployment.

## What is Anaconda?

Anaconda is a distribution of Python and R programming languages for scientific computing, data science, and machine learning. It provides:

- Easy package management with conda
- Environment management to isolate different projects
- A simpler way to install packages with complex dependencies
- Cross-platform compatibility (Windows, macOS, Linux)

## Local Development Setup

### 1. Install Anaconda or Miniconda

First, download and install Anaconda or Miniconda for your operating system:

- [Anaconda Installation Guide](https://docs.anaconda.com/free/anaconda/install/index.html)
- [Miniconda Installation Guide](https://docs.conda.io/en/latest/miniconda.html)

Miniconda is recommended if you want a minimal installation.

### 2. Create the Trinity Environment

Once Anaconda is installed, open a terminal (Anaconda Prompt on Windows) and create a new environment for the Trinity project:

```bash
conda create -n trinity python=3.11
```

This creates a new conda environment named "trinity" with Python 3.11.

### 3. Activate the Environment

Activate the environment to use it:

```bash
conda activate trinity
```

Your command prompt should change to indicate you're now in the trinity environment.

### 4. Install Dependencies

With the environment activated, navigate to your project directory and install the required dependencies:

```bash
cd path/to/trinity-server
pip install -r requirements.txt
```

### 5. Set Up Environment Variables

Create and configure your `.env` file:

```bash
cp .env.example .env
# Edit the .env file with your API keys and settings
```

### 6. Run the Application

With the environment activated and configured, you can run the server:

```bash
python run.py
```

## Common Conda Commands

Here are some useful conda commands for managing your environment:

```bash
# List all conda environments
conda env list

# Update conda itself
conda update conda

# Install a specific package in the current environment
conda install package_name

# Remove a package
conda remove package_name

# Export your environment to a file
conda env export > environment.yml

# Create an environment from a file
conda env create -f environment.yml

# Remove an environment
conda env remove -n trinity
```

## Using Anaconda in Production

For production environments, you can:

1. Use the same conda environments approach on your server
2. Export your environment to an environment.yml file for reproducibility
3. Configure systemd to use the conda environment as shown in the deployment guide

## Troubleshooting

### Common Issues and Solutions

1. **Conda command not found**
   - Ensure Anaconda is added to your PATH
   - Restart your terminal or shell

2. **Package conflicts**
   - Use `conda install package_name=version` to install specific versions
   - Create a new environment if conflicts can't be resolved

3. **Environment activation issues in systemd**
   - Ensure the full path to conda is used in the ExecStart command
   - Use absolute paths in the systemd service file

4. **Slow conda operations**
   - Consider using Miniconda instead of full Anaconda
   - Run `conda clean --all` to clean up caches

## Additional Resources

- [Conda User Guide](https://docs.conda.io/projects/conda/en/latest/user-guide/index.html)
- [Conda Cheat Sheet](https://docs.conda.io/projects/conda/en/latest/user-guide/cheatsheet.html)
- [Anaconda Documentation](https://docs.anaconda.com/) 