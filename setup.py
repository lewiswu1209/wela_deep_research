
from setuptools import setup
from setuptools import find_packages

if __name__ == "__main__":
	with open("requirements.txt", "r") as f:
		requirements = f.read().splitlines()

	with open("README.md", "r") as f:
		long_description = f.read()

	setup(
		name = "wela_deep_research",
		version = "0.0.2",
		packages = find_packages(),
		entry_points={
			"console_scripts": [
				"research = wela_deep_research.research:main",
			]
		},
		install_requires = requirements,
		description="A clone of Wela, a researcher.",
		long_description = long_description,
		long_description_content_type = "text/markdown",
		author = "Lewis Wu",
		author_email = "lewiswu1209@163.com",
		license = "MIT",
		url = "https://github.com/lewiswu1209/wela_deep_research.git"
	)
