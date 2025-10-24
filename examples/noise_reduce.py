"""Reduce background noise in an audio file using noise reduction."""
from pathlib import Path
import click
import soundfile as sf
import librosa
import noisereduce as nr
from tqdm import tqdm
from pydub import AudioSegment
import numpy as np
import tempfile
import os
import time


def process_segment(samples: np.ndarray, 
                   sr: int,
                   noise_sample: np.ndarray,
                   reduction_strength: float = 0.15,
                   stationary: bool = True) -> np.ndarray:
    """Apply noise reduction to a segment of audio."""
    return nr.reduce_noise(
        y=samples,
        sr=sr,
        y_noise=noise_sample,
        prop_decrease=reduction_strength,
        n_jobs=1,
        stationary=stationary,
        chunk_size=6000,
        padding=3000
    )

def preview_noise_reduction(samples: np.ndarray,
                          sr: int,
                          preview_start_ms: int,
                          preview_duration_ms: int,
                          noise_sample: np.ndarray,
                          reduction_strength: float) -> str:
    """Create a preview of noise reduction and play it."""
    # Extract preview segment
    start_idx = int(preview_start_ms * sr / 1000)
    duration_idx = int(preview_duration_ms * sr / 1000)
    preview_segment = samples[start_idx:start_idx + duration_idx]
    
    # Process preview
    preview_reduced = process_segment(preview_segment, sr, noise_sample, reduction_strength)
    
    # Save preview to temp file
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tf:
        preview_path = tf.name
        preview_reduced = np.int16(preview_reduced * 32767)
        preview_segment = AudioSegment(
            preview_reduced.tobytes(),
            frame_rate=sr,
            sample_width=2,
            channels=1
        )
        preview_segment.export(preview_path, format='wav')
    
    return preview_path

def reduce_noise(input_path: str,
                noise_start_ms: int = 0,
                noise_duration_ms: int = 1000,
                output_path: str = None,
                reduction_strength: float = 0.15,
                preview_mode: bool = False,
                preview_start_ms: int = None,
                preview_duration_ms: int = 5000) -> str:  # 5-second preview default
    """
    Reduce background noise in an audio file while preserving voice.
    
    Args:
        input_path: Path to input audio file
        noise_start_ms: Start time of noise sample in milliseconds
        noise_duration_ms: Duration of noise sample in milliseconds
        output_path: Where to save the result (default: input_name_clean.mp3)
        reduction_strength: Strength of noise reduction (0.0 to 1.0, default 0.15 for voice)
    """
    # Load the audio file using pydub first
    click.echo("Loading audio file...")
    audio = AudioSegment.from_file(input_path)
    
    # Convert to numpy array
    samples = np.array(audio.get_array_of_samples())
    if audio.channels == 2:
        samples = samples.reshape((-1, 2))
        samples = samples.mean(axis=1)  # Convert to mono
    
    # Convert to float32
    samples = samples.astype(np.float32) / (2**15 if samples.dtype == np.int16 else 2**31)
    sr = audio.frame_rate
    
    # Convert milliseconds to samples
    noise_start = int(noise_start_ms * sr / 1000)
    noise_end = noise_start + int(noise_duration_ms * sr / 1000)
    
    # Get noise profile from the specified section
    noise_sample = samples[noise_start:noise_end]
    
    if preview_mode:
        if preview_start_ms is None:
            # Default to middle of file for preview
            total_duration_ms = len(samples) * 1000 / sr
            preview_start_ms = int(total_duration_ms * 0.4)  # 40% into file
        
        click.echo(f"Creating preview at {preview_start_ms/1000:.1f}s...")
        preview_path = preview_noise_reduction(
            samples, sr, preview_start_ms, preview_duration_ms,
            noise_sample, reduction_strength
        )
        return preview_path

    # Apply gentle noise reduction optimized for voice
    click.echo("Applying noise reduction (voice-optimized)...")
    try:
        reduced = process_segment(samples, sr, noise_sample, reduction_strength)
    except Exception as e:
        click.echo(f"Error during noise reduction: {e}", err=True)
        # Fallback to even gentler method
        click.echo("Trying fallback method...")
        reduced = process_segment(samples, sr, noise_sample, reduction_strength * 0.5)
    
    # Generate output path if not provided
    if not output_path:
        p = Path(input_path)
        output_path = str(p.parent / f"{p.stem}_clean{p.suffix}")
    
    # Convert back to int16 for saving
    reduced = np.int16(reduced * 32767)
    
    # Save using pydub
    click.echo("Saving cleaned audio...")
    reduced_segment = AudioSegment(
        reduced.tobytes(), 
        frame_rate=sr,
        sample_width=2,
        channels=1
    )
    reduced_segment.export(output_path, format=Path(output_path).suffix.lstrip('.'))
    return output_path


@click.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--noise-start', '-s', default=0,
              help='Start time of noise sample in milliseconds')
@click.option('--noise-duration', '-d', default=1000,
              help='Duration of noise sample in milliseconds')
@click.option('--strength', '-r', default=0.15,
              help='Noise reduction strength (0.0 to 1.0, default 0.15 for voice)')
@click.option('--output', '-o', type=click.Path(),
              help='Output file path (default: input_name_clean.mp3)')
@click.option('--preview/--no-preview', default=False,
              help='Create a preview of settings on a short segment')
@click.option('--preview-start', default=None, type=int,
              help='Start time for preview in milliseconds (default: 40% into file)')
@click.option('--preview-duration', default=5000,
              help='Duration of preview in milliseconds (default: 5000)')
def main(input_file, noise_start, noise_duration, strength, output, 
         preview, preview_start, preview_duration):
    """Remove background noise from an audio file.
    
    Specify a section of audio that contains only background noise (no speech/music)
    using --noise-start and --noise-duration. This will be used as the noise profile.
    
    Use --preview to test settings on a short segment before processing the whole file.
    
    Examples:
    
    # Preview noise reduction (5 seconds from 40% into file):
    python noise_reduce.py input.mp3 --preview
    
    # Preview specific section with custom strength:
    python noise_reduce.py input.mp3 --preview --preview-start 10000 --strength 0.2
    
    # Process full file after finding good settings:
    python noise_reduce.py input.mp3 --noise-start 0 --noise-duration 2000 --strength 0.2
    """
    try:
        output_path = reduce_noise(
            input_file,
            noise_start,
            noise_duration,
            output,
            strength,
            preview,
            preview_start,
            preview_duration
        )
        
        if preview:
            click.echo(f"\nCreated preview file: {output_path}")
            click.echo("\nPreview cleanup will happen in 30 seconds...")
            
            # Let user listen to preview
            time.sleep(30)
            
            # Cleanup preview file
            try:
                os.unlink(output_path)
                click.echo("Preview file cleaned up")
            except:
                pass
        else:
            click.echo(f"Created noise-reduced file: {output_path}")
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


if __name__ == '__main__':
    main()