import requests
import base64
import json

def mermaid_to_svg(mermaid_code, output_file=None):
    """
    Convert Mermaid diagram code to SVG using Mermaid's online API.
    
    Args:
        mermaid_code (str): The Mermaid diagram code
        output_file (str, optional): Path to save the SVG file
        
    Returns:
        str: The SVG content
    """
    
    # Mermaid Ink API endpoint
    url = "https://mermaid.ink/svg/"
    
    # Encode the mermaid code to base64
    encoded = base64.urlsafe_b64encode(mermaid_code.encode('utf-8')).decode('ascii').rstrip('=')
    
    # Make the request
    response = requests.get(f"{url}{encoded}")
    
    if response.status_code == 200:
        svg_content = response.text
        
        # Save to file if specified
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(svg_content)
            print(f"SVG saved to {output_file}")
        
        return svg_content
    else:
        raise Exception(f"API request failed with status code {response.status_code}")


# Example usage
if __name__ == "__main__":
    # Example Mermaid flowchart
    with open(r'C:\Users\itayb\Documents\vsProjects\MATH\Collatz\new\3-26.mmd', "r") as f:
        mermaid_code = f.read()
    
        try:
            # Get SVG content
            svg = mermaid_to_svg(mermaid_code, "diagram.svg")
            print("SVG generated successfully!")
            print(f"SVG length: {len(svg)} characters")
            
        except Exception as e:
            print(f"Error: {e}")


# Alternative: Using Mermaid's kroki API
def mermaid_to_svg_kroki(mermaid_code, output_file=None):
    """
    Alternative method using Kroki API.
    
    Args:
        mermaid_code (str): The Mermaid diagram code
        output_file (str, optional): Path to save the SVG file
        
    Returns:
        str: The SVG content
    """
    
    url = "https://kroki.io/mermaid/svg"
    
    headers = {
        'Content-Type': 'text/plain'
    }
    
    response = requests.post(url, data=mermaid_code, headers=headers)
    
    if response.status_code == 200:
        svg_content = response.text
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(svg_content)
            print(f"SVG saved to {output_file}")
        
        return svg_content
    else:
        raise Exception(f"API request failed with status code {response.status_code}")