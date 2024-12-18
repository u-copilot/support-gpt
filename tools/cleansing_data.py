import os
import shutil
from bs4 import BeautifulSoup
import lxml


def extract_text_from_html(html_content):
    """Extract and clean text from HTML content."""
    soup = BeautifulSoup(html_content, "lxml")
    # Remove script and style elements
    for script_or_style in soup(["script", "style"]):
        script_or_style.decompose()
    # Get text
    text = soup.get_text()
    # Break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # Break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # Drop blank lines
    text = "\n".join(chunk for chunk in chunks if chunk)
    return text


def convert_path_to_url(file_path):
    # Define the keyword to search in the file path
    keyword = "website"

    # Split the path by the keyword and keep the part after it
    parts = file_path.split(keyword)
    relative_path = parts[1] if len(parts) > 1 else ""

    # Replace all '/' with '___' in the relative path
    formatted_path = relative_path.replace("/", "___")

    # Ensure there's no leading '___'
    formatted_path = formatted_path.lstrip("___")

    return formatted_path


def process_directory(source_dir, target_dir):
    """Process all HTML files in the source directory and save the cleaned text to the target directory."""
    for subdir, dirs, files in os.walk(source_dir):
        print("subdir=", subdir)
        print("dirs=", dirs)
        print("files=", files)
        for file in files:
            file_path = os.path.join(subdir, file)
            print("file_path=", file_path)
            if file_path.endswith(".html"):
                print("file_path=", file_path)
                try:
                    with open(file_path, "r", encoding="utf-8") as file2:
                        html_content = file2.read()
                        # print('html_content=', html_content)
                except OSError as e:
                    print(f"Error opening file: {e}")
                except IOError as e:
                    print(f"Error reading file: {e}")
                except Exception as e:
                    print(f"An unexpected error occurred: {e}")

                cleaned_text = extract_text_from_html(html_content)
                print("cleaned_text=", cleaned_text)
                # Define the path for the cleaned text
                relative_path = os.path.relpath(subdir, source_dir)
                save_dir = os.path.join(target_dir, relative_path)
                if not os.path.exists(save_dir):
                    print("NO DIR !!!")
                    os.makedirs(save_dir)

                print("save_dir=", save_dir)
                # print('file=',os.path.splitext(file))
                print("file=", file)

                # print(os.path.splitext(file)[0] + '.html')
                # save_path = os.path.join(save_dir, os.path.splitext(file)[0] + '.html')
                # save_path = os.path.join(save_dir, file)
                save_path = os.path.join(save_dir, convert_path_to_url(file_path))
                try:
                    with open(save_path, "w", encoding="utf-8") as text_file:
                        text_file.write(cleaned_text)
                    print(f"Processed {file_path} -> {save_path}")
                except OSError as e:
                    print(f"Error opening file: {e}")
                except IOError as e:
                    print(f"Error reading file: {e}")
                except Exception as e:
                    print(f"An unexpected error occurred: {e}")

            elif file_path.endswith(".pdf"):
                print("file_path =", file_path)

                # Define the relative and target paths
                relative_path = os.path.relpath(
                    subdir, source_dir
                )  # Preserve folder structure
                save_dir = os.path.join(target_dir, relative_path)

                # Ensure the target directory exists
                if not os.path.exists(save_dir):
                    print("NO DIR !!!")
                    os.makedirs(save_dir)

                print("save_dir =", save_dir)

                # Define source and destination paths
                source_path = file_path  # Original PDF file
                save_path = os.path.join(
                    save_dir, convert_path_to_url(file_path)
                )  # Target PDF file path

                try:
                    # Copy the PDF file
                    shutil.copy2(
                        source_path, save_path
                    )  # copy2 preserves metadata (e.g., timestamps)
                    print(f"Copied {source_path} -> {save_path}")
                except Exception as e:
                    print(f"Error copying file: {e}")

            # elif file_path.endswith('.pdf'):
            #     print('file_path=', file_path)
            #     try:
            #         with open(file_path, 'r', encoding='utf-8') as file2:
            #             html_content = file2.read()
            #             # print('html_content=', html_content)
            #     except OSError as e:
            #         print(f"Error opening file: {e}")
            #     except IOError as e:
            #         print(f"Error reading file: {e}")
            #     except Exception as e:
            #         print(f"An unexpected error occurred: {e}")

            #     cleaned_text = extract_text_from_html(html_content)
            #     print('cleaned_text=', cleaned_text)

            #     # Define the path for the cleaned text
            #     relative_path = os.path.relpath(subdir, source_dir)
            #     save_dir = os.path.join(target_dir, relative_path)
            #     if not os.path.exists(save_dir):
            #         print('NO DIR !!!')
            #         os.makedirs(save_dir)

            #     print('save_dir=',save_dir)
            #     # print('file=',os.path.splitext(file))
            #     print('file=', file)

            #     save_path = os.path.join(save_dir, convert_path_to_url(file_path))
            #     try:
            #         with open(save_path, 'wb') as pdf_file:
            #             pdf_file.write(cleaned_text.encode('utf-8'))
            #         print(f"Processed {file_path} -> {save_path}")
            #     except OSError as e:
            #         print(f"Error opening file: {e}")
            #     except IOError as e:
            #         print(f"Error reading file: {e}")
            #     except Exception as e:
            #         print(f"An unexpected error occurred: {e}")


# Define the source and target directories
source_directory = "website/"
target_directory = "cleansed_website/"

# Run the processing function
process_directory(source_directory, target_directory)
