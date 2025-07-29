import librosa
import numpy as np
import matplotlib.pyplot as plt
import cv2
import os
from pyzbar.pyzbar import decode
from pyzbar.pyzbar import ZBarSymbol
from scipy.interpolate import interp1d


def extract_qr_from_audio(audio_path, outdir="output", tempdir="temp"):
    qr_code_image = get_spectrogram(audio_path)

    image_filename = os.path.join(tempdir, "qr_image_sayori.png")
    cv2.imwrite(image_filename, qr_code_image)
    print(f"Saved qr code to {image_filename}")

    detector = cv2.QRCodeDetector()
    data, vertices_array, _ = detector.detectAndDecode(qr_code_image)

    if vertices_array is not None:
        print("Success: QR detected")
        print(f"Content: {data}")

    else:
        print("QR detection failed")


def get_spectrogram(audio_path: str):
    y, sr = librosa.load(audio_path, sr=None)
    print(f"Loaded {audio_path} at {sr} Hz")

    # Standard STFT
    S = np.abs(librosa.stft(y, n_fft=4096, hop_length=1024))
    S_db = librosa.amplitude_to_db(S, ref=np.max)

    # Get the frequency axis
    freqs = librosa.fft_frequencies(sr=sr, n_fft=4096)

    # Select 9000–22000 Hz (linear scale)
    mask = (freqs >= 9200) & (freqs <= 22000)
    S_db_crop = S_db[mask, :]
    freqs_crop = freqs[mask]

    # Now resample the cropped spectrogram vertically using a log scale
    num_log_bins = 256  # higher number -> higher vertical resolution
    log_freqs = np.geomspace(freqs_crop[0], freqs_crop[-1], num=num_log_bins)

    # Interpolate rows to log scale
    interp_func = interp1d(freqs_crop, S_db_crop, axis=0, kind="linear")
    S_log = interp_func(log_freqs)

    # Normalize to 0–255
    img = 255 * (S_log - S_log.min()) / np.ptp(S_log)
    img = img.astype(np.uint8)
    img = np.flipud(img)

    # Resize to square image and add black border
    h, w = img.shape
    qr_code_image = cv2.resize(img, (2 * h, 2 * h), interpolation=cv2.INTER_AREA)
    qr_code_image = cv2.copyMakeBorder(
        qr_code_image, 20, 20, 20, 20, borderType=cv2.BORDER_CONSTANT, value=0
    )

    # improve borders
    qr_code_image = cv2.medianBlur(qr_code_image, 7)
    _, qr_code_image = cv2.threshold(qr_code_image, 180, 255, cv2.THRESH_BINARY)

    # qr decoders work best in black on white
    qr_code_image = cv2.bitwise_not(qr_code_image)

    return qr_code_image
