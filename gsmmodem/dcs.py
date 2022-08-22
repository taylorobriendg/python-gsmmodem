# -*- coding: utf-8 -*-

""" Data Coding Scheme related utility methods.
For details of the GSM standard, see https://en.wikipedia.org/wiki/Data_Coding_Scheme """

from enum import Enum, auto
from .pdu import decodeGsm7, unpackSeptets, decodeUcs2

class Charset(Enum):
    GSM_7_BIT = auto()
    EIGHT_BIT_DATA = auto()
    UCS2 = auto()
    RESERVED = auto()
    UNDEFINED = auto()


def dcsToCharset(dcs):
    """See 3GPP TS 23.038 V9.1.1 (2010-02)"""
    
    bits_7t4 = dcs >> 4
    bits_3t0 = dcs & 0x0f
    if   bits_7t4 <= 0b0000:
        return Charset.GSM_7_BIT
    elif bits_7t4 <= 0b0001:
        if bits3t0 == 0b0000:
            # TODO:
            # GSM 7 bit default alphabet; message preceded by language indication.
            # The first 3 characters of the message are a two-character representation of the
            # language encoded according to ISO 639 [12], followed by a CR character. The
            # CR character is then followed by 90 characters of text.
            return Charset.GSM_7_BIT
        elif bits3t0 == 0b0001:
            # TODO:
            # UCS2; message preceded by language indication
            # The message starts with a two GSM 7-bit default alphabet character
            # representation of the language encoded according to ISO 639 [12]. This is padded
            # to the octet boundary with two bits set to 0 and then followed by 40 characters of
            # UCS2-encoded message.
            # An MS not supporting UCS2 coding will present the two character language
            # identifier followed by improperly interpreted user data. 
            return Charset.UCS2
        else:
            return Charset.UNDEFINED
    elif (bits_7t4 == 0b0010) or (bits_7t4 == 0b0011):
        return Charset.GSM_7_BIT
    elif bits_7t4 <= 0b0111:
        # TODO:
        # Bit 5, if set to 0, indicates the text is uncompressed
        # Bit 5, if set to 1, indicates the text is compressed using the compression algorithm defined in
        # 3GPP TS 23.042 [13]
        return [ Charset.GSM_7_BIT,
                 Charset.EIGHT_BIT_DATA,
                 Charset.UCS2,
                 Charset.RESERVED ][bits_3t0 >> 2]
    elif bits_7t4 == 0b1000:
        return Charset.RESERVED
    elif bits_7t4 == 0b1001:
        return [ Charset.GSM_7_BIT,
                 Charset.EIGHT_BIT_DATA,
                 Charset.UCS2,
                 Charset.RESERVED ][bits_3t0 >> 2]
    elif bits_7t4 <= 0b1100:
        return Charset.RESERVED
    elif bits_7t4 <= 0b1101:
        # TODO: I1 protocol message defined in 3GPP TS 24.294 [19] 
        return Charset.RESERVED
    elif bits_7t4 <= 0b1110:
        # TODO: Defined by the WAP Forum [15] 
        return Charset.RESERVED
    elif bits_7t4 <= 0b1111:
        bit2 = (bits_3t0 & 0b0100) >> 2
        if bit2:
            Charset.EIGHT_BIT_DATA
        else:
            Charset.GSM_7_BIT


def decodeWithDcs(data, dcs, logger = None):
    charset = dcsToCharset(dcs)
    logger.debug('dcs = ' + str(dcs))
    logger.debug('charset = ' + str(charset))
    logger.debug('data = ' + str(data))
    retval = None
    dataBytes = bytes.fromhex(data)
    if charset == Charset.GSM_7_BIT:
        retval = decodeGsm7(unpackSeptets(dataBytes))
    elif charset == Charset.UCS2:
        retval = decodeUcs2(iter(dataBytes), len(dataBytes))
    elif charset == Charset.EIGHT_BIT_DATA:
        retval = data
    else:
        # RESERVED
        # UNDEFINED
        if logger:
            logger.debug('decodeWithDcs(): Unable to determine the encoding from the DCS data, returning the data as if it is 8-bit data anyway.')
        retval = data

    return retval
