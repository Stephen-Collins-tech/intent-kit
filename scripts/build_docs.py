#!/usr/bin/env python3
"""
Static documentation builder for Intent Kit.

This script converts Markdown documentation to static HTML for GitHub Pages deployment.
"""

import os
import re
import shutil
from pathlib import Path
from typing import Dict, List, Optional

import markdown
from jinja2 import Environment, FileSystemLoader


class StaticDocBuilder:
    """Builds static documentation from Markdown files."""
    
    def __init__(self, docs_dir: str = "docs", output_dir: str = "docs-site"):
        self.docs_dir = Path(docs_dir)
        self.output_dir = Path(output_dir)
        self.template_dir = Path("scripts/templates")
        
        # Create template environment
        self.env = Environment(loader=FileSystemLoader(str(self.template_dir)))
        
        # Configure markdown
        self.md = markdown.Markdown(
            extensions=[
                'markdown.extensions.toc',
                'markdown.extensions.codehilite',
                'markdown.extensions.fenced_code',
                'markdown.extensions.tables',
                'markdown.extensions.admonition',
            ],
            extension_configs={
                'markdown.extensions.codehilite': {
                    'css_class': 'highlight',
                    'use_pygments': True,
                }
            }
        )
        
        # Navigation structure (matching mkdocs.yml)
        self.nav_structure = [
            {"Home": "index.md"},
            {"Quickstart": "quickstart.md"},
            {
                "Core Concepts": [
                    {"Overview": "concepts/index.md"},
                    {"Intent Graphs": "concepts/intent-graphs.md"},
                    {"Nodes and Actions": "concepts/nodes-and-actions.md"},
                    {"Context Architecture": "concepts/context-architecture.md"},
                    {"Context Management": "concepts/context-management.md"},
                    {"DAG Validation": "concepts/dag-validation.md"},
                    {"Extractor Nodes": "concepts/extractor-nodes.md"},
                    {"Clarification Nodes": "concepts/clarification-nodes.md"},
                ]
            },
            {
                "API Reference": [
                    {"API Reference": "api/api-reference.md"},
                ]
            },
            {
                "Configuration": [
                    {"Overview": "configuration/index.md"},
                    {"JSON Serialization": "configuration/json-serialization.md"},
                    {"LLM Integration": "configuration/llm-integration.md"},
                ]
            },
            {
                "Services": [
                    {"AI Services": "services/ai-services.md"},
                ]
            },
            {
                "Utilities": [
                    {"Utilities": "utils/utilities.md"},
                ]
            },
            {
                "Examples": [
                    {"Overview": "examples/index.md"},
                    {"Basic Examples": "examples/basic-examples.md"},
                    {"Calculator Bot": "examples/calculator-bot.md"},
                    {"Context-Aware Chatbot": "examples/context-aware-chatbot.md"},
                    {"Context Memory Demo": "examples/context-memory-demo.md"},
                    {"DAG Examples": "examples/dag-examples.md"},
                    {"JSON Demo": "examples/json-demo.md"},
                ]
            },
            {
                "Development": [
                    {"Overview": "development/index.md"},
                    {"Building": "development/building.md"},
                    {"Testing": "development/testing.md"},
                    {"Evaluation": "development/evaluation.md"},
                    {"Evaluation Framework": "development/evaluation-framework.md"},
                    {"Debugging": "development/debugging.md"},
                    {"Performance Monitoring": "development/performance-monitoring.md"},
                    {"Documentation Management": "development/documentation-management.md"},
                ]
            },
        ]
    
    def build(self):
        """Build the complete static documentation site."""
        print("Building static documentation...")
        
        # Clean output directory
        if self.output_dir.exists():
            shutil.rmtree(self.output_dir)
        self.output_dir.mkdir(parents=True)
        
        # Copy assets
        self._copy_assets()
        
        # Copy robots.txt
        self._copy_robots_txt()
        
        # Build navigation
        nav_data = self._build_navigation()
        
        # Process all markdown files
        self._process_markdown_files(nav_data)
        
        # Process 404 page separately
        self._process_404_page()
        
        # Create sitemap
        self._create_sitemap()
        
        print(f"Documentation built successfully in {self.output_dir}")
    
    def _copy_assets(self):
        """Copy CSS, JS, and other assets."""
        # Copy any existing assets from docs directory
        assets_src = self.docs_dir / "assets"
        if assets_src.exists():
            assets_dest = self.output_dir / "assets"
            shutil.copytree(assets_src, assets_dest)
        
        # Create basic CSS if it doesn't exist
        css_file = self.output_dir / "assets" / "style.css"
        css_file.parent.mkdir(parents=True, exist_ok=True)
        
        if not css_file.exists():
            with open(css_file, "w") as f:
                f.write(self._get_default_css())
    
    def _copy_robots_txt(self):
        """Copy robots.txt file."""
        robots_src = self.docs_dir / "robots.txt"
        if robots_src.exists():
            robots_dest = self.output_dir / "robots.txt"
            shutil.copy2(robots_src, robots_dest)
            print("Copied: robots.txt")
    
    def _get_default_css(self) -> str:
        """Get default CSS styles."""
        return """
/* Intent Kit Documentation Styles */
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    line-height: 1.6;
    color: #333;
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

.nav {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 8px;
    margin-bottom: 2rem;
}

.nav ul {
    list-style: none;
    padding: 0;
    margin: 0;
}

.nav li {
    margin: 0.5rem 0;
}

.nav a {
    text-decoration: none;
    color: #007bff;
}

.nav a:hover {
    text-decoration: underline;
}

.content {
    background: white;
    padding: 2rem;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

h1, h2, h3, h4, h5, h6 {
    color: #2c3e50;
    margin-top: 2rem;
    margin-bottom: 1rem;
}

h1 {
    border-bottom: 3px solid #3498db;
    padding-bottom: 0.5rem;
}

code {
    background: #f8f9fa;
    padding: 0.2rem 0.4rem;
    border-radius: 4px;
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}

pre {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 8px;
    overflow-x: auto;
    border-left: 4px solid #3498db;
}

pre code {
    background: none;
    padding: 0;
}

table {
    border-collapse: collapse;
    width: 100%;
    margin: 1rem 0;
}

th, td {
    border: 1px solid #ddd;
    padding: 0.75rem;
    text-align: left;
}

th {
    background: #f8f9fa;
    font-weight: bold;
}

.admonition {
    padding: 1rem;
    margin: 1rem 0;
    border-radius: 8px;
    border-left: 4px solid;
}

.admonition.note {
    background: #e3f2fd;
    border-color: #2196f3;
}

.admonition.warning {
    background: #fff3e0;
    border-color: #ff9800;
}

.admonition.danger {
    background: #ffebee;
    border-color: #f44336;
}

.breadcrumb {
    margin-bottom: 1rem;
    color: #666;
}

.breadcrumb a {
    color: #007bff;
    text-decoration: none;
}

.breadcrumb a:hover {
    text-decoration: underline;
}
"""
    
    def _build_navigation(self) -> Dict:
        """Build navigation data structure."""
        nav_data = {"pages": []}
        
        def process_nav_item(item, parent_path=""):
            if isinstance(item, dict):
                for title, content in item.items():
                    if isinstance(content, str):
                        # Single page
                        file_path = content
                        url_path = file_path.replace('.md', '.html')
                        nav_data["pages"].append({
                            "title": title,
                            "file": file_path,
                            "url": url_path,
                            "path": parent_path
                        })
                    elif isinstance(content, list):
                        # Section with subpages
                        section = {"title": title, "pages": []}
                        for subitem in content:
                            process_nav_item(subitem, f"{parent_path}/{title}" if parent_path else title)
                        nav_data["pages"].append(section)
        
        for item in self.nav_structure:
            process_nav_item(item)
        
        return nav_data
    
    def _process_markdown_files(self, nav_data: Dict):
        """Process all markdown files and convert to HTML."""
        for page_info in nav_data["pages"]:
            if isinstance(page_info, dict) and "file" in page_info:
                self._process_single_file(page_info, nav_data)
    
    def _process_single_file(self, page_info: Dict, nav_data: Dict):
        """Process a single markdown file."""
        md_file = self.docs_dir / page_info["file"]
        if not md_file.exists():
            print(f"Warning: {md_file} not found")
            return
        
        # Read markdown content
        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # Convert to HTML
        html_content = self.md.convert(md_content)
        
        # Extract title from first h1 or filename
        title = page_info["title"]
        title_match = re.search(r'<h1[^>]*>(.*?)</h1>', html_content)
        if title_match:
            title = title_match.group(1)
        
        # Generate breadcrumb
        breadcrumb = self._generate_breadcrumb(page_info["path"])
        
        # Render with template
        template = self.env.get_template('page.html')
        html_output = template.render(
            title=title,
            content=html_content,
            navigation=nav_data,
            breadcrumb=breadcrumb,
            current_page=page_info["url"]
        )
        
        # Write output file
        output_file = self.output_dir / page_info["url"]
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_output)
        
        print(f"Built: {page_info['url']}")
    
    def _generate_breadcrumb(self, path: str) -> List[Dict]:
        """Generate breadcrumb navigation."""
        if not path:
            return []
        
        parts = path.split('/')
        breadcrumb = []
        current_path = ""
        
        for part in parts:
            current_path = f"{current_path}/{part}" if current_path else part
            breadcrumb.append({
                "title": part,
                "url": f"{current_path.lower().replace(' ', '-')}.html"
            })
        
        return breadcrumb
    
    def _process_404_page(self):
        """Process the 404 page separately."""
        md_file = self.docs_dir / "404.md"
        if not md_file.exists():
            print("Warning: 404.md not found")
            return
        
        # Read markdown content
        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # Convert to HTML
        html_content = self.md.convert(md_content)
        
        # Render with template (simplified for 404)
        template = self.env.get_template('page.html')
        html_output = template.render(
            title="Page Not Found",
            content=html_content,
            navigation={"pages": []},  # No navigation for 404
            breadcrumb=[],
            current_page="404.html"
        )
        
        # Write output file
        output_file = self.output_dir / "404.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_output)
        
        print("Built: 404.html")
    
    def _create_sitemap(self):
        """Create a sitemap.xml file."""
        sitemap_content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
"""
        
        # Add all HTML files to sitemap
        for html_file in self.output_dir.rglob("*.html"):
            relative_path = html_file.relative_to(self.output_dir)
            url = f"https://stephen-collins-tech.github.io/intent-kit/{relative_path}"
            sitemap_content += f"""  <url>
    <loc>{url}</loc>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>
"""
        
        sitemap_content += "</urlset>"
        
        with open(self.output_dir / "sitemap.xml", 'w') as f:
            f.write(sitemap_content)


def main():
    """Main entry point."""
    builder = StaticDocBuilder()
    builder.build()


if __name__ == "__main__":
    main()