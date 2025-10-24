"""Duplicate an MP3 file content N times and save with suffix."""
from pathlib import Path
import sys
import click
from pydub import AudioSegment
import shutil


def duplicate_audio(input_path: str, n_times: int = 100) -> str:
    """Load audio file, duplicate its content n times, and save with suffix."""
    # Load the audio file
    audio = AudioSegment.from_file(input_path)
    
    # Duplicate the content n times
    duplicated = audio * n_times
    
    # Generate output path with _N suffix before extension
    p = Path(input_path)
    output_path = p.parent / f"{p.stem}_{n_times}{p.suffix}"
    
    # Export
    duplicated.export(str(output_path), format='mp3')
    return str(output_path)


def check_ffmpeg():
    """Verify ffmpeg is available."""
    if not shutil.which('ffmpeg'):
        click.echo("Error: ffmpeg not found. Please install ffmpeg and make sure it's in your PATH.", err=True)
        click.echo("On Windows, try: winget install --id Gyan.FFmpeg")
        click.echo("Then restart your terminal/PowerShell")
        sys.exit(1)

@click.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--times', '-n', default=100, help='Number of times to duplicate the content')
def main(input_file, times):
    """Duplicate an audio file content N times and save with _N suffix."""
    check_ffmpeg()
    try:
        input_path = Path(input_file).resolve()
        if not input_path.exists():
            click.echo(f"Error: File not found: {input_path}", err=True)
            sys.exit(1)
        output = duplicate_audio(str(input_path), times)
        click.echo(f"Created {output}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


if __name__ == '__main__':
    main()



# python .\examples\duplicate_audio.py ".\tests\Putna dova.mp3" --times 100