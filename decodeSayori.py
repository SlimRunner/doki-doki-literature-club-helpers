import librosa
import numpy as np
import matplotlib.pyplot as plt
import cv2
from pyzbar.pyzbar import decode
from pyzbar.pyzbar import ZBarSymbol


def extract_qr_from_audio(audio_path):
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
    num_log_bins = 256  # or 256 for higher vertical resolution
    log_freqs = np.geomspace(freqs_crop[0], freqs_crop[-1], num=num_log_bins)

    # Interpolate rows to log scale
    from scipy.interpolate import interp1d

    interp_func = interp1d(freqs_crop, S_db_crop, axis=0, kind="linear")
    S_log = interp_func(log_freqs)

    # Normalize to 0–255
    img = 255 * (S_log - S_log.min()) / np.ptp(S_log)
    img = img.astype(np.uint8)
    img = np.flipud(img)

    # Resize to square image
    h, w = img.shape
    img_resized = cv2.resize(img, (2 * h, 2 * h), interpolation=cv2.INTER_AREA)
    img_2_decode = cv2.copyMakeBorder(
        img_resized, 20, 20, 20, 20, borderType=cv2.BORDER_CONSTANT, value=0
    )
    img_2_decode = cv2.medianBlur(img_2_decode, 7)
    _, img_2_decode = cv2.threshold(
        img_2_decode, 180, 255, cv2.THRESH_BINARY
    )  # + cv2.THRESH_OTSU

    cv2.imwrite("qr_candidate_logstft.png", img_2_decode)
    print("Saved qr_candidate_logstft.png")

    detector = cv2.QRCodeDetector()
    data, vertices_array, binary_qrcode = detector.detectAndDecode(img_2_decode)

    if vertices_array is not None:
        print(data)
    else:
        print("NONE")

    decoded = decode(img_2_decode, symbols=[ZBarSymbol.QRCODE])
    if decoded:
        print("✅ QR Detected!")
        for d in decoded:
            print("➡️", d.data.decode())
    else:
        print("❌ Not detected.")


if __name__ == "__main__":
    extract_qr_from_audio("input.ogg")
