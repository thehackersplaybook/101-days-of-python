import argparse
import cv2
import sys
import os
from rich.console import Console
from rich.text import Text
import base64
import mimetypes
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env", override=True)

console = Console()

client = Anthropic()


def print_banner() -> None:
    """
    Prints the banner for the program.

    Args:
        None

    Returns:
        None
    """

    banner = Text(
        """
    ***************************************
    *    Face Emotion Detector Program    *
    ***************************************
    """,
        style="bold magenta",
    )
    console.print(banner)


def image_to_base64(image_path: str) -> str:
    """
    Converts an image given it's file path to base64 encoded string.

    Args:
        image_path (str): Path to the image file.

    Returns:
        str: Base64 encoded string of the image.
    """

    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
    return encoded_string


def detect_emotion(file_path: str) -> str:
    """
    Detects the emotion of the person in the image.

    Args:
        file_path (str): Path to the image file.

    Returns:
        str: Detected emotion.
    """

    media_type = detect_media_type(file_path)
    image_data = image_to_base64(file_path)
    message = client.messages.create(
        model="claude-3-7-sonnet-20250219",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_data,
                        },
                    },
                    {
                        "type": "text",
                        "text": "Detect the emotion of the person in the image. Respond only with the emotion as a string.",
                    },
                ],
            }
        ],
    )
    return message.content[0].text


def detect_media_type(file_path: str) -> str:
    """
    Detects the media type of the file.

    Args:
        file_path (str): Path to the file.

    Returns:
        str: Media type of the file.
    """

    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type and mime_type.startswith("image/"):
        return mime_type
    return "unknown"


def print_emotion(emotion: str) -> None:
    """
    Prints the detected emotion.

    Args:
        emotion (str): Detected emotion.

    Returns:
        None
    """
    
    console.print(f"Detected Emotion: {emotion}", style="bold green")


def main():
    print_banner()

    parser = argparse.ArgumentParser(description="Face Emotion Detector")
    parser.add_argument("--face-path", type=str, help="Path to the face image")
    parser.add_argument("--live", action="store_true", help="Start live camera mode")

    args = parser.parse_args()

    if args.face_path:
        emotion = detect_emotion(args.face_path)
        print_emotion(emotion)
    elif args.live:
        cap = cv2.VideoCapture(0)
        console.print("Press 'Enter' to capture an image.", style="bold yellow")
        while True:
            ret, frame = cap.read()
            cv2.imshow("Live Camera", frame)
            if cv2.waitKey(1) & 0xFF == ord("\r"):
                image_path = "captured_image.jpg"
                cv2.imwrite(image_path, frame)
                console.print(
                    f"Image captured and saved to {image_path}", style="bold cyan"
                )
                emotion = detect_emotion(image_path)
                console.print(f"Detected Emotion: {emotion}", style="bold green")
                os.remove(image_path)
                console.print(
                    f"Temporary image {image_path} deleted.", style="bold red"
                )
                break
        cap.release()
        cv2.destroyAllWindows()
    else:
        console.print(
            "Please provide either --face-path or --live option.", style="bold red"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()