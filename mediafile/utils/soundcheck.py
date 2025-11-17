# iTunes Sound Check encoding.


import binascii
import codecs
import math
import struct


def sc_decode(soundcheck):
    """Convert a Sound Check bytestring value to a (gain, peak) tuple as
    used by ReplayGain.
    """
    # We decode binary data. If one of the formats gives us a text
    # string, interpret it as UTF-8.
    if isinstance(soundcheck, str):
        soundcheck = soundcheck.encode("utf-8")

    # SoundCheck tags consist of 10 numbers, each represented by 8
    # characters of ASCII hex preceded by a space.
    try:
        soundcheck = codecs.decode(soundcheck.replace(b" ", b""), "hex")
        soundcheck = struct.unpack("!iiiiiiiiii", soundcheck)
    except (struct.error, TypeError, binascii.Error):
        # SoundCheck isn't in the format we expect, so return default
        # values.
        return 0.0, 0.0

    # SoundCheck stores absolute calculated/measured RMS value in an
    # unknown unit. We need to find the ratio of this measurement
    # compared to a reference value of 1000 to get our gain in dB. We
    # play it safe by using the larger of the two values (i.e., the most
    # attenuation).
    maxgain = max(soundcheck[:2])
    if maxgain > 0:
        gain = math.log10(maxgain / 1000.0) * -10
    else:
        # Invalid gain value found.
        gain = 0.0

    # SoundCheck stores peak values as the actual value of the sample,
    # and again separately for the left and right channels. We need to
    # convert this to a percentage of full scale, which is 32768 for a
    # 16 bit sample. Once again, we play it safe by using the larger of
    # the two values.
    peak = max(soundcheck[6:8]) / 32768.0

    return round(gain, 2), round(peak, 6)


def sc_encode(gain, peak):
    """Encode ReplayGain gain/peak values as a Sound Check string."""
    # SoundCheck stores the peak value as the actual value of the
    # sample, rather than the percentage of full scale that RG uses, so
    # we do a simple conversion assuming 16 bit samples.
    peak *= 32768.0

    # SoundCheck stores absolute RMS values in some unknown units rather
    # than the dB values RG uses. We can calculate these absolute values
    # from the gain ratio using a reference value of 1000 units. We also
    # enforce the maximum and minimum value here, which is equivalent to
    # about -18.2dB and 30.0dB.
    g1 = int(min(round((10 ** (gain / -10)) * 1000), 65534)) or 1
    # Same as above, except our reference level is 2500 units.
    g2 = int(min(round((10 ** (gain / -10)) * 2500), 65534)) or 1

    # The purpose of these values are unknown, but they also seem to be
    # unused so we just use zero.
    uk = 0
    values = (g1, g1, g2, g2, uk, uk, int(peak), int(peak), uk, uk)
    return (" %08X" * 10) % values
