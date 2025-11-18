# Results processing pipeline for the Integrated Annual Business Survey

This repository is a copy of the Research and Development results processing pipeline. It is not intended for production but will be used for development of new tools and processes.

---

## Installation

Make sure you have git and Python installed on your computer (using Service Now) and set up python and pip using these instructions [ASAP wiki](https://gitlab-app-l-01/ASAP/coding-getting-started-guide/-/wikis/python).


The version of python used in this project is Python 3.11, so follow the ASAP instructions above to create a `.bat` file that will enable you to access that version of Python using `python3_11`.

> **🟢 Best Practice:** If you have multiple Python versions installed, you can specify the Python version uv should use when creating the environment. See the next section for details.

---

## 1. Cloning this repo

Open your terminal in the folder you want to save your repo in. Note that you don't need to create a folder for the name of the repo, cloning will automatically do this.
Input the following line into your terminal:

```sh
git clone https://github.com/ONSdigital/r_and_d_experimental.git
```

---

## 2. Installing uv for the virtual environment and package management

This section can be skipped if you have performed it for a different project.

### Detail on installation


> **pipx:**
> pipx stands for "pip for applications". It is a tool specifically designed to install and run Python command-line applications in isolated environments while making them globally accessible.

#### Why do we use pipx instead of pip to install uv?


> **Why not pip for uv?**
> If you use `pip install uv`, uv will be installed in your base Python environment. This can cause dependency conflicts with other projects. If you update or uninstall something, or switch Python version (3.11 → 3.12), uv may stop working because it was installed in the old environment.


> **Solution:**
> pipx installs command line interface tools in their own sandbox environments but makes them globally accessible. This keeps your CLI tools stable and independent of your main Python environment.

#### What is uv?


> **What is uv?**
> uv is a modern, fast Python package (alternative to pip, conda) and project manager written in Rust. It is recommended for managing dependencies and environments in modern Python projects.

---

In order to install uv on your Windows machine so it is not restricted to a particular environment, use pipx. You may first need to install pipx:

```sh
python3_11 -m pip install pipx
```
To ensure your environment PATH is updated, run the following:
```sh
python3_11 -m pipx ensurepath
```
After this you will need to restart your terminal.

You are now ready to install uv:
```sh
python3_11 -m pipx install uv
```
and again update your path:
```sh
python3_11 -m pipx ensurepath
```
Again, restart your terminal, and now `uv` will be available globally.

> **💡 Tip:** Always restart your terminal after running `ensurepath` to make sure new tools are available globally.

---


> **Artifactory Authentication Best Practice:**
> To ensure `uv` uses the ONS Artifactory and the ONSApps version of Python, create a `uv.toml` file in your Roaming directory as described below. Never share your encrypted password or uv.toml file publicly.


Access 'Roaming' folder by pasting the following path in the navigation bar in Windows Explorer or by navigating to:
```
C:\Users<windows_username>\AppData\Roaming
```
> **Note:** Replace `windows_username` with your actual Windows username (e.g., `C:\Users\abcde\AppData\Roaming`).

Create a folder named 'uv' inside Roaming directory:
```
C:\Users<windows_username>\AppData\Roaming\uv
```
> **Note:** Again, use your real Windows username in the path above.

Inside the uv folder, create a file named uv.toml and paste in the following.

replacing `<username>` and `<encr_password>` with your windows username and encrypted password respectively.

```toml
cache-dir = "D:/uv/cache"

allow-insecure-host = ["onsart-01"]
python-preference = "only-system"
python-downloads = "never"

[[index]]
url = "https://<username>:<encr_password>@onsart-01/artifactory/api/pypi/yr-python/simple"
default = true
```

---




## 3. Creating a virtual environment and installing packages using uv

> **Best Practice:** Use uv to automatically create and manage your virtual environment for Python projects. This avoids manual setup and ensures all dependencies are handled consistently.

To ensure the environment uses Python 3.11, run:
```sh
uv venv --python="C:\ONSapps\My_Python\Python_3_11"
```
(Replace with the path to where you have python installed, if necessary)
```sh

To activate the environment, run this:
```sh
.venv\Scripts\activate
```
Finally, install the project dependancies with this command
```sh
uv sync --all-extras
```

> **What happens?**
> The above commands will create or update the `.venv` virtual environment in your project folder using Python 3.11 and install all dependencies, including every optional extra defined in `pyproject.toml`, ensuring a complete development setup.

To activate the environment, run this:
```sh
.venv\Scripts\activate
```

You will now have a new folder named `.venv` at the root level of your repo to contain the version of Python and all other items to install for this project.


---


## 4. Pre-commit actions

> **Best Practice:** Use pre-commit hooks to maintain code quality and security. This repository contains a configuration of pre-commit hooks that are language agnostic and focused on repository security and coding style.

If approaching this project as a developer, you should install and enable `pre-commits` by running the following in your shell:

```sh
pre-commit install
```

Once pre-commits are activated, whenever you commit to this repository a series of checks will be executed. If any of these checks fail, the commit will be rejected and you will be prompted to fix the issues, stage the files and commit again.

> **Tip:** Run `pre-commit run --all-files` before your first commit to catch issues early.

---

## Tool Comparison Table

Choosing the right tool is essential for a stable and efficient workflow. Here’s how pip, pipx, and uv compare:

| Tool   | Purpose                                      | Isolation | Global CLI | Speed | Dependency Management | Recommended Use |
|--------|----------------------------------------------|-----------|------------|-------|----------------------|-----------------|
| pip    | Install Python packages                      | No        | No         | Medium| Yes                  | Libraries       |
| pipx   | Install Python CLI apps in isolated envs     | Yes       | Yes        | Medium| Limited              | CLI tools       |
| uv     | Modern, fast package/project manager (Rust)  | Yes       | Yes        | Fast  | Yes                  | Projects/CLI    |

> **Best Practice:** Use pipx for CLI tools and uv for project management to keep your global Python environment clean and avoid dependency conflicts.

---


# License

<!-- Unless stated otherwise, the codebase is released under [the MIT Licence][mit]. -->

The code, unless otherwise stated, is released under [the MIT Licence][mit].

The documentation for this work is subject to [© 2024 Crown Copyright (Office for National Statistics)][copyright] and is available under the terms of the [Open Government 3.0][ogl] licence.

[mit]: https://gitlab-app-l-01/ashe-group/sandpit/-/blob/main/LICENSE
[copyright]: http://www.nationalarchives.gov.uk/information-management/re-using-public-sector-information/uk-government-licensing-framework/crown-copyright/
[ogl]: http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/
