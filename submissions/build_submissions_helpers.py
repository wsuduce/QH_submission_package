#!/usr/bin/env python3
"""
Helper functions for markdown to LaTeX conversion
"""
import re

def process_markdown_text(text):
    """Convert basic markdown formatting to LaTeX"""
    if not text:
        return ""
    
    # Clean up the text
    text = text.strip()
    
    # Convert bold **text** to \textbf{text}
    text = re.sub(r'\*\*(.*?)\*\*', r'\\textbf{\1}', text)
    
    # Convert italic *text* to \textit{text}
    text = re.sub(r'(?<!\*)\*([^*]+?)\*(?!\*)', r'\\textit{\1}', text)
    
    # Convert citations [1] to \cite{ref1}
    text = re.sub(r'\[(\d+)\]', r'~\\cite{ref\1}', text)
    
    # Handle math mode - preserve existing LaTeX math
    # Don't modify content inside $ or \( \) or align environments
    
    # Convert markdown links [text](url) but preserve LaTeX figure refs
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)(?![{])', r'\1', text)  # Remove links, keep text
    
    # Convert em-dashes and special characters
    text = text.replace('—', '---')
    text = text.replace('–', '--')
    text = text.replace('"', '``')
    text = text.replace('"', "''")
    
    # Handle lists
    lines = text.split('\n')
    processed_lines = []
    in_itemize = False
    
    for line in lines:
        if line.strip().startswith('•') or line.strip().startswith('*') or line.strip().startswith('-'):
            if not in_itemize:
                processed_lines.append('\\begin{itemize}')
                in_itemize = True
            item_text = line.strip()[1:].strip()  # Remove bullet
            processed_lines.append(f'\\item {item_text}')
        else:
            if in_itemize:
                processed_lines.append('\\end{itemize}')
                in_itemize = False
            if line.strip():
                processed_lines.append(line)
    
    if in_itemize:
        processed_lines.append('\\end{itemize}')
    
    return '\n'.join(processed_lines)

def process_markdown_sections(lines):
    """Convert markdown sections to LaTeX"""
    content = []
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip metadata and version stamps
        if line.startswith('**Manuscript ID:**') or line.startswith('**Change set:**') or line.startswith('<!--'):
            i += 1
            continue
        
        # Handle headers
        if line.startswith('###'):
            title = line[3:].strip()
            title = process_markdown_text(title)
            content.append(f'\\subsection{{{title}}}')
            
        elif line.startswith('##'):
            title = line[2:].strip()
            title = process_markdown_text(title)
            if title.startswith('Appendix'):
                content.append(f'\\appendix')
                title = title.replace('Appendix', '').strip()
                if title:
                    content.append(f'\\section{{{title}}}')
            else:
                content.append(f'\\section{{{title}}}')
                
        elif line.startswith('#') and not line.startswith('##'):
            # Skip main title - already in template
            pass
            
        # Handle figures
        elif line.startswith('!['):
            # Extract figure info: ![caption](path){options}
            fig_match = re.match(r'!\[(.*?)\]\((.*?)\)(?:\{(.*?)\})?', line)
            if fig_match:
                caption = fig_match.group(1)
                path = fig_match.group(2)
                
                # Extract filename from path
                filename = path.split('/')[-1]
                
                content.append('\\begin{figure}[htbp]')
                content.append('\\centering')
                content.append(f'\\includegraphics[width=0.9\\textwidth]{{{filename}}}')
                content.append(f'\\caption{{{process_markdown_text(caption)}}}')
                content.append('\\end{figure}')
        
        # Handle regular text
        elif line:
            # Collect paragraph until empty line
            paragraph_lines = [line]
            j = i + 1
            while j < len(lines) and lines[j].strip() and not lines[j].strip().startswith('#') and not lines[j].strip().startswith('!['):
                paragraph_lines.append(lines[j])
                j += 1
            
            paragraph = '\n'.join(paragraph_lines)
            processed_paragraph = process_markdown_text(paragraph)
            
            if processed_paragraph:
                content.append(processed_paragraph)
            
            i = j - 1  # Adjust for the loop increment
        
        i += 1
    
    return '\n\n'.join(content)
