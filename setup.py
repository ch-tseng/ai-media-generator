from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="ai-media-generator",
    version="1.0.0",
    author="AI Media Generator Contributors",
    description="一個整合多個AI服務的媒體生成工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/ai-media-generator",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    include_package_data=True,
    package_data={
        "": ["*.html", "*.css", "*.js", "*.png", "*.svg", "*.ico"],
    },
    entry_points={
        "console_scripts": [
            "ai-media-generator=app_ai_generate:main",
        ],
    },
) 