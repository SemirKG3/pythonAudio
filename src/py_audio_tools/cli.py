import click
from .processor import AudioProcessor


@click.group()
def main():
    """py-audio-tools CLI"""


@main.command()
@click.argument("input", type=click.Path(exists=True))
@click.option("--start-ms", type=int, default=0)
@click.option("--end-ms", type=int, default=None)
@click.option("-o", "--output", type=click.Path(), default="out.wav")
def trim(input, start_ms, end_ms, output):
    """Trim an audio file between start-ms and end-ms and write to output."""
    ap = AudioProcessor()
    audio = ap.load(input)
    trimmed = ap.trim(audio, start_ms, end_ms)
    out = ap.export(trimmed, output)
    click.echo(f"Wrote {out}")


if __name__ == "__main__":
    main()
