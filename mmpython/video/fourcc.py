#if 0
# $Id$
# $Log$
# Revision 1.3  2003/05/13 12:31:43  the_krow
# + Copyright Notice
#
#
# MMPython - Media Metadata for Python
# Copyright (C) 2003 Thomas Schueppel
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MER-
# CHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
# 
# -----------------------------------------------------------------------
#endif

RIFFWAVE = {}
RIFFCODEC = {}

RIFFWAVE[0x0000] = 'Microsoft Unknown Wave Format';
RIFFWAVE[0x0001] = 'Microsoft Pulse Code Modulation (PCM)';
RIFFWAVE[0x0002] = 'Microsoft ADPCM';
RIFFWAVE[0x0003] = 'IEEE Float';
RIFFWAVE[0x0004] = 'Compaq Computer VSELP';
RIFFWAVE[0x0005] = 'IBM CVSD';
RIFFWAVE[0x0006] = 'Microsoft A-Law';
RIFFWAVE[0x0007] = 'Microsoft mu-Law';
RIFFWAVE[0x0010] = 'OKI ADPCM';
RIFFWAVE[0x0011] = 'Intel DVI/IMA ADPCM';
RIFFWAVE[0x0012] = 'Videologic MediaSpace ADPCM';
RIFFWAVE[0x0013] = 'Sierra Semiconductor ADPCM';
RIFFWAVE[0x0014] = 'Antex Electronics G.723 ADPCM';
RIFFWAVE[0x0015] = 'DSP Solutions DigiSTD';
RIFFWAVE[0x0016] = 'DSP Solutions DigiFIX';
RIFFWAVE[0x0017] = 'Dialogic OKI ADPCM';
RIFFWAVE[0x0018] = 'MediaVision ADPCM';
RIFFWAVE[0x0019] = 'Hewlett-Packard CU';
RIFFWAVE[0x0020] = 'Yamaha ADPCM';
RIFFWAVE[0x0021] = 'Speech Compression Sonarc';
RIFFWAVE[0x0022] = 'DSP Group TrueSpeech';
RIFFWAVE[0x0023] = 'Echo Speech EchoSC1';
RIFFWAVE[0x0024] = 'Audiofile AF36';
RIFFWAVE[0x0025] = 'Audio Processing Technology APTX';
RIFFWAVE[0x0026] = 'AudioFile AF10';
RIFFWAVE[0x0027] = 'Prosody 1612';
RIFFWAVE[0x0028] = 'LRC';
RIFFWAVE[0x0030] = 'Dolby AC2';
RIFFWAVE[0x0031] = 'Microsoft GSM 6.10';
RIFFWAVE[0x0032] = 'MSNAudio';
RIFFWAVE[0x0033] = 'Antex Electronics ADPCME';
RIFFWAVE[0x0034] = 'Control Resources VQLPC';
RIFFWAVE[0x0035] = 'DSP Solutions DigiREAL';
RIFFWAVE[0x0036] = 'DSP Solutions DigiADPCM';
RIFFWAVE[0x0037] = 'Control Resources CR10';
RIFFWAVE[0x0038] = 'Natural MicroSystems VBXADPCM';
RIFFWAVE[0x0039] = 'Crystal Semiconductor IMA ADPCM';
RIFFWAVE[0x003A] = 'EchoSC3';
RIFFWAVE[0x003B] = 'Rockwell ADPCM';
RIFFWAVE[0x003C] = 'Rockwell Digit LK';
RIFFWAVE[0x003D] = 'Xebec';
RIFFWAVE[0x0040] = 'Antex Electronics G.721 ADPCM';
RIFFWAVE[0x0041] = 'G.728 CELP';
RIFFWAVE[0x0042] = 'MSG723';
RIFFWAVE[0x0050] = 'Microsoft MPEG';
RIFFWAVE[0x0052] = 'RT24';
RIFFWAVE[0x0053] = 'PAC';
RIFFWAVE[0x0055] = 'MPEG Layer 3';
RIFFWAVE[0x0059] = 'Lucent G.723';
RIFFWAVE[0x0060] = 'Cirrus';
RIFFWAVE[0x0061] = 'ESPCM';
RIFFWAVE[0x0062] = 'Voxware';
RIFFWAVE[0x0063] = 'Canopus Atrac';
RIFFWAVE[0x0064] = 'G.726 ADPCM';
RIFFWAVE[0x0065] = 'G.722 ADPCM';
RIFFWAVE[0x0066] = 'DSAT';
RIFFWAVE[0x0067] = 'DSAT Display';
RIFFWAVE[0x0069] = 'Voxware Byte Aligned';
RIFFWAVE[0x0070] = 'Voxware AC8';
RIFFWAVE[0x0071] = 'Voxware AC10';
RIFFWAVE[0x0072] = 'Voxware AC16';
RIFFWAVE[0x0073] = 'Voxware AC20';
RIFFWAVE[0x0074] = 'Voxware MetaVoice';
RIFFWAVE[0x0075] = 'Voxware MetaSound';
RIFFWAVE[0x0076] = 'Voxware RT29HW';
RIFFWAVE[0x0077] = 'Voxware VR12';
RIFFWAVE[0x0078] = 'Voxware VR18';
RIFFWAVE[0x0079] = 'Voxware TQ40';
RIFFWAVE[0x0080] = 'Softsound';
RIFFWAVE[0x0081] = 'Voxware TQ60';
RIFFWAVE[0x0082] = 'MSRT24';
RIFFWAVE[0x0083] = 'G.729A';
RIFFWAVE[0x0084] = 'MVI MV12';
RIFFWAVE[0x0085] = 'DF G.726';
RIFFWAVE[0x0086] = 'DF GSM610';
RIFFWAVE[0x0088] = 'ISIAudio';
RIFFWAVE[0x0089] = 'Onlive';
RIFFWAVE[0x0091] = 'SBC24';
RIFFWAVE[0x0092] = 'Dolby AC3 SPDIF';
RIFFWAVE[0x0097] = 'ZyXEL ADPCM';
RIFFWAVE[0x0098] = 'Philips LPCBB';
RIFFWAVE[0x0099] = 'Packed';
RIFFWAVE[0x0100] = 'Rhetorex ADPCM';
RIFFWAVE[0x0101] = 'IBM mu-law';
RIFFWAVE[0x0102] = 'IBM A-law';
RIFFWAVE[0x0103] = 'IBM AVC Adaptive Differential Pulse Code Modulation (ADPCM)';
RIFFWAVE[0x0111] = 'Vivo G.723';
RIFFWAVE[0x0112] = 'Vivo Siren';
RIFFWAVE[0x0123] = 'Digital G.723';
RIFFWAVE[0x0140] = 'Windows Media Video V8';
RIFFWAVE[0x0161] = 'Windows Media Audio V7 / V8 / V9';
RIFFWAVE[0x0162] = 'Windows Media Audio Professional V9';
RIFFWAVE[0x0163] = 'Windows Media Audio Lossless V9';
RIFFWAVE[0x0200] = 'Creative Labs ADPCM';
RIFFWAVE[0x0202] = 'Creative Labs Fastspeech8';
RIFFWAVE[0x0203] = 'Creative Labs Fastspeech10';
RIFFWAVE[0x0220] = 'Quarterdeck';
RIFFWAVE[0x0300] = 'FM Towns Snd';
RIFFWAVE[0x0300] = 'Fujitsu FM Towns Snd';
RIFFWAVE[0x0400] = 'BTV Digital';
RIFFWAVE[0x0680] = 'VME VMPCM';
RIFFWAVE[0x1000] = 'Olivetti GSM';
RIFFWAVE[0x1001] = 'Olivetti ADPCM';
RIFFWAVE[0x1002] = 'Olivetti CELP';
RIFFWAVE[0x1003] = 'Olivetti SBC';
RIFFWAVE[0x1004] = 'Olivetti OPR';
RIFFWAVE[0x1100] = 'Lernout & Hauspie LH Codec';
RIFFWAVE[0x1400] = 'Norris';
RIFFWAVE[0x1401] = 'AT&T ISIAudio';
RIFFWAVE[0x1500] = 'Soundspace Music Compression';
RIFFWAVE[0x2000] = 'AC3';
RIFFWAVE[0x7A21] = 'GSM-AMR (CBR, no SID)';
RIFFWAVE[0x7A22] = 'GSM-AMR (VBR, including SID)';
RIFFWAVE[0xFFFF] = 'development';

RIFFCODEC['3IV1'] = '3ivx v1'
RIFFCODEC['3IV2'] = '3ivx v2'
RIFFCODEC['AASC'] = 'Autodesk Animator'
RIFFCODEC['ABYR'] = 'Kensington ?ABYR?'
RIFFCODEC['AEMI'] = 'Array VideoONE MPEG1-I Capture'
RIFFCODEC['AFLC'] = 'Autodesk Animator FLC'
RIFFCODEC['AFLI'] = 'Autodesk Animator FLI'
RIFFCODEC['AMPG'] = 'Array VideoONE MPEG'
RIFFCODEC['ANIM'] = 'Intel RDX (ANIM)'
RIFFCODEC['AP41'] = 'AngelPotion Definitive'
RIFFCODEC['ASV1'] = 'Asus Video v1'
RIFFCODEC['ASV2'] = 'Asus Video v2'
RIFFCODEC['ASVX'] = 'Asus Video 2.0 (audio)'
RIFFCODEC['AUR2'] = 'Aura 2 Codec - YUV 4:2:2'
RIFFCODEC['AURA'] = 'Aura 1 Codec - YUV 4:1:1'
RIFFCODEC['BINK'] = 'RAD Game Tools Bink Video'
RIFFCODEC['BT20'] = 'Conexant Prosumer Video'
RIFFCODEC['BTCV'] = 'Conexant Composite Video Codec'
RIFFCODEC['BW10'] = 'Data Translation Broadway MPEG Capture'
RIFFCODEC['CC12'] = 'Intel YUV12'
RIFFCODEC['CDVC'] = 'Canopus DV'
RIFFCODEC['CFCC'] = 'Digital Processing Systems DPS Perception'
RIFFCODEC['CGDI'] = 'Microsoft Office 97 Camcorder Video'
RIFFCODEC['CHAM'] = 'Winnov Caviara Champagne'
RIFFCODEC['CJPG'] = 'Creative WebCam JPEG'
RIFFCODEC['CLJR'] = 'Cirrus Logic YUV 4 pixels'
RIFFCODEC['CMYK'] = 'Common Data Format in Printing'
RIFFCODEC['CPLA'] = 'Weitek 4:2:0 YUV Planar'
RIFFCODEC['CRAM'] = 'Microsoft Video 1 (CRAM)'
RIFFCODEC['CVID'] = 'Radius Cinepak'
RIFFCODEC['CWLT'] = '?CWLT?'
RIFFCODEC['CWLT'] = 'Microsoft Color WLT DIB'
RIFFCODEC['CYUV'] = 'Creative Labs YUV'
RIFFCODEC['CYUY'] = 'ATI YUV'
RIFFCODEC['D261'] = 'H.261'
RIFFCODEC['D263'] = 'H.263'
RIFFCODEC['DIV3'] = 'DivX v3 MPEG-4 Low-Motion'
RIFFCODEC['DIV4'] = 'DivX v3 MPEG-4 Fast-Motion'
RIFFCODEC['DIV5'] = '?DIV5?'
RIFFCODEC['DIVX'] = 'DivX v4'
RIFFCODEC['divx'] = 'DivX'
RIFFCODEC['DMB1'] = 'Matrox Rainbow Runner hardware MJPEG'
RIFFCODEC['DMB2'] = 'Paradigm MJPEG'
RIFFCODEC['DSVD'] = '?DSVD?'
RIFFCODEC['DUCK'] = 'Duck True Motion 1.0'
RIFFCODEC['DVAN'] = '?DVAN?'
RIFFCODEC['DVE2'] = 'InSoft DVE-2 Videoconferencing'
RIFFCODEC['dvsd'] = 'DV'
RIFFCODEC['DVSD'] = 'DV'
RIFFCODEC['DVX1'] = 'DVX1000SP Video Decoder'
RIFFCODEC['DVX2'] = 'DVX2000S Video Decoder'
RIFFCODEC['DVX3'] = 'DVX3000S Video Decoder'
RIFFCODEC['DX50'] = 'DivX v5'
RIFFCODEC['DXT1'] = 'Microsoft DirectX Compressed Texture (DXT1)'
RIFFCODEC['DXT2'] = 'Microsoft DirectX Compressed Texture (DXT2)'
RIFFCODEC['DXT3'] = 'Microsoft DirectX Compressed Texture (DXT3)'
RIFFCODEC['DXT4'] = 'Microsoft DirectX Compressed Texture (DXT4)'
RIFFCODEC['DXT5'] = 'Microsoft DirectX Compressed Texture (DXT5)'
RIFFCODEC['DXTC'] = 'Microsoft DirectX Compressed Texture (DXTC)'
RIFFCODEC['EKQ0'] = 'Elsa ?EKQ0?'
RIFFCODEC['ELK0'] = 'Elsa ?ELK0?'
RIFFCODEC['ESCP'] = 'Eidos Escape'
RIFFCODEC['ETV1'] = 'eTreppid Video ETV1'
RIFFCODEC['ETV2'] = 'eTreppid Video ETV2'
RIFFCODEC['ETVC'] = 'eTreppid Video ETVC'
RIFFCODEC['FLJP'] = 'D-Vision Field Encoded Motion JPEG'
RIFFCODEC['FRWA'] = 'SoftLab-Nsk Forward Motion JPEG w/ alpha channel'
RIFFCODEC['FRWD'] = 'SoftLab-Nsk Forward Motion JPEG'
RIFFCODEC['FVF1'] = 'Iterated Systems Fractal Video Frame'
RIFFCODEC['GLZW'] = 'Motion LZW (gabest@freemail.hu)'
RIFFCODEC['GPEG'] = 'Motion JPEG (gabest@freemail.hu)'
RIFFCODEC['GWLT'] = 'Microsoft Greyscale WLT DIB'
RIFFCODEC['H260'] = 'Intel ITU H.260 Videoconferencing'
RIFFCODEC['H261'] = 'Intel ITU H.261 Videoconferencing'
RIFFCODEC['H262'] = 'Intel ITU H.262 Videoconferencing'
RIFFCODEC['H263'] = 'Intel ITU H.263 Videoconferencing'
RIFFCODEC['H264'] = 'Intel ITU H.264 Videoconferencing'
RIFFCODEC['H265'] = 'Intel ITU H.265 Videoconferencing'
RIFFCODEC['H266'] = 'Intel ITU H.266 Videoconferencing'
RIFFCODEC['H267'] = 'Intel ITU H.267 Videoconferencing'
RIFFCODEC['H268'] = 'Intel ITU H.268 Videoconferencing'
RIFFCODEC['H269'] = 'Intel ITU H.269 Videoconferencing'
RIFFCODEC['HFYU'] = 'Huffman Lossless Codec'
RIFFCODEC['HMCR'] = 'Rendition Motion Compensation Format (HMCR)'
RIFFCODEC['HMRR'] = 'Rendition Motion Compensation Format (HMRR)'
RIFFCODEC['i263'] = 'Intel ITU H.263 Videoconferencing (i263)'
RIFFCODEC['I420'] = 'Intel Indeo 4'
RIFFCODEC['IAN '] = 'Intel RDX'
RIFFCODEC['ICLB'] = 'InSoft CellB Videoconferencing'
RIFFCODEC['IGOR'] = 'Power DVD'
RIFFCODEC['IJPG'] = 'Intergraph JPEG'
RIFFCODEC['ILVC'] = 'Intel Layered Video'
RIFFCODEC['ILVR'] = 'ITU-T H.263+'
RIFFCODEC['IPDV'] = 'I-O Data Device Giga AVI DV Codec'
RIFFCODEC['IR21'] = 'Intel Indeo 2.1'
RIFFCODEC['IRAW'] = 'Intel YUV Uncompressed'
RIFFCODEC['IV30'] = 'Ligos Indeo 3.0'
RIFFCODEC['IV31'] = 'Ligos Indeo 3.1'
RIFFCODEC['IV32'] = 'Ligos Indeo 3.2'
RIFFCODEC['IV33'] = 'Ligos Indeo 3.3'
RIFFCODEC['IV34'] = 'Ligos Indeo 3.4'
RIFFCODEC['IV35'] = 'Ligos Indeo 3.5'
RIFFCODEC['IV36'] = 'Ligos Indeo 3.6'
RIFFCODEC['IV37'] = 'Ligos Indeo 3.7'
RIFFCODEC['IV38'] = 'Ligos Indeo 3.8'
RIFFCODEC['IV39'] = 'Ligos Indeo 3.9'
RIFFCODEC['IV40'] = 'Ligos Indeo Interactive 4.0'
RIFFCODEC['IV41'] = 'Ligos Indeo Interactive 4.1'
RIFFCODEC['IV42'] = 'Ligos Indeo Interactive 4.2'
RIFFCODEC['IV43'] = 'Ligos Indeo Interactive 4.3'
RIFFCODEC['IV44'] = 'Ligos Indeo Interactive 4.4'
RIFFCODEC['IV45'] = 'Ligos Indeo Interactive 4.5'
RIFFCODEC['IV46'] = 'Ligos Indeo Interactive 4.6'
RIFFCODEC['IV47'] = 'Ligos Indeo Interactive 4.7'
RIFFCODEC['IV48'] = 'Ligos Indeo Interactive 4.8'
RIFFCODEC['IV49'] = 'Ligos Indeo Interactive 4.9'
RIFFCODEC['IV50'] = 'Ligos Indeo Interactive 5.0'
RIFFCODEC['JBYR'] = 'Kensington ?JBYR?'
RIFFCODEC['JPEG'] = 'Still Image JPEG DIB'
RIFFCODEC['JPGL'] = 'Webcam JPEG Light?'
RIFFCODEC['KMVC'] = 'Karl Morton\'s Video Codec'
RIFFCODEC['LEAD'] = 'LEAD Video Codec'
RIFFCODEC['Ljpg'] = 'LEAD MJPEG Codec'
RIFFCODEC['M261'] = 'Microsoft H.261'
RIFFCODEC['M263'] = 'Microsoft H.263'
RIFFCODEC['M4S2'] = 'Microsoft MPEG-4 (M4S2)'
RIFFCODEC['m4s2'] = 'Microsoft MPEG-4 (m4s2)'
RIFFCODEC['MC12'] = 'ATI Motion Compensation Format (MC12)'
RIFFCODEC['MCAM'] = 'ATI Motion Compensation Format (MCAM)'
RIFFCODEC['MJ2C'] = 'Morgan Multimedia Motion JPEG2000'
RIFFCODEC['mJPG'] = 'IBM Motion JPEG w/ Huffman Tables'
RIFFCODEC['MJPG'] = 'Motion JPEG DIB'
RIFFCODEC['MP42'] = 'Microsoft MPEG-4 (low-motion)'
RIFFCODEC['MP43'] = 'Microsoft MPEG-4 (fast-motion)'
RIFFCODEC['MP4S'] = 'Microsoft MPEG-4 (MP4S)'
RIFFCODEC['mp4s'] = 'Microsoft MPEG-4 (mp4s)'
RIFFCODEC['MPEG'] = 'MPEG 1 Video I-Frame'
RIFFCODEC['MPG4'] = 'Microsoft MPEG-4 Video High Speed Compressor'
RIFFCODEC['MPGI'] = 'Sigma Designs MPEG'
RIFFCODEC['MRCA'] = 'FAST Multimedia Mrcodec'
RIFFCODEC['MRCA'] = 'Martin Regen Codec'
RIFFCODEC['MRLE'] = 'Microsoft RLE'
RIFFCODEC['MRLE'] = 'Run Length Encoding'
RIFFCODEC['MSVC'] = 'Microsoft Video 1'
RIFFCODEC['MTX1'] = 'Matrox ?MTX1?'
RIFFCODEC['MTX2'] = 'Matrox ?MTX2?'
RIFFCODEC['MTX3'] = 'Matrox ?MTX3?'
RIFFCODEC['MTX4'] = 'Matrox ?MTX4?'
RIFFCODEC['MTX5'] = 'Matrox ?MTX5?'
RIFFCODEC['MTX6'] = 'Matrox ?MTX6?'
RIFFCODEC['MTX7'] = 'Matrox ?MTX7?'
RIFFCODEC['MTX8'] = 'Matrox ?MTX8?'
RIFFCODEC['MTX9'] = 'Matrox ?MTX9?'
RIFFCODEC['MV12'] = '?MV12?'
RIFFCODEC['MWV1'] = 'Aware Motion Wavelets'
RIFFCODEC['nAVI'] = '?nAVI?'
RIFFCODEC['NTN1'] = 'Nogatech Video Compression 1'
RIFFCODEC['NVS0'] = 'nVidia GeForce Texture (NVS0)'
RIFFCODEC['NVS1'] = 'nVidia GeForce Texture (NVS1)'
RIFFCODEC['NVS2'] = 'nVidia GeForce Texture (NVS2)'
RIFFCODEC['NVS3'] = 'nVidia GeForce Texture (NVS3)'
RIFFCODEC['NVS4'] = 'nVidia GeForce Texture (NVS4)'
RIFFCODEC['NVS5'] = 'nVidia GeForce Texture (NVS5)'
RIFFCODEC['NVT0'] = 'nVidia GeForce Texture (NVT0)'
RIFFCODEC['NVT1'] = 'nVidia GeForce Texture (NVT1)'
RIFFCODEC['NVT2'] = 'nVidia GeForce Texture (NVT2)'
RIFFCODEC['NVT3'] = 'nVidia GeForce Texture (NVT3)'
RIFFCODEC['NVT4'] = 'nVidia GeForce Texture (NVT4)'
RIFFCODEC['NVT5'] = 'nVidia GeForce Texture (NVT5)'
RIFFCODEC['PDVC'] = 'I-O Data Device Digital Video Capture DV codec'
RIFFCODEC['PGVV'] = 'Radius Video Vision'
RIFFCODEC['PHMO'] = 'IBM Photomotion'
RIFFCODEC['PIM1'] = 'Pegasus Imaging ?PIM1?'
RIFFCODEC['PIM2'] = 'Pegasus Imaging ?PIM2?'
RIFFCODEC['PIMJ'] = 'Pegasus Imaging Lossless JPEG'
RIFFCODEC['PVEZ'] = 'Horizons Technology PowerEZ'
RIFFCODEC['PVMM'] = 'PacketVideo Corporation MPEG-4'
RIFFCODEC['PVW2'] = 'Pegasus Imaging Wavelet Compression'
RIFFCODEC['QPEG'] = 'Q-Team QPEG 1.0'
RIFFCODEC['qpeq'] = 'Q-Team QPEG 1.1'
RIFFCODEC['RGBT'] = 'Computer Concepts 32-bit support'
RIFFCODEC['RLE '] = 'Microsoft Run Length Encoder'
RIFFCODEC['RLE4'] = 'Run Length Encoded 4'
RIFFCODEC['RLE8'] = 'Run Length Encoded 8'
RIFFCODEC['RT21'] = 'Intel Indeo 2.1'
RIFFCODEC['RT21'] = 'Intel Real Time Video 2.1'
RIFFCODEC['rv20'] = 'RealVideo G2'
RIFFCODEC['rv30'] = 'RealVideo 8'
RIFFCODEC['RVX '] = 'Intel RDX (RVX )'
RIFFCODEC['s422'] = 'Tekram VideoCap C210 YUV 4:2:2'
RIFFCODEC['SDCC'] = 'Sun Communication Digital Camera Codec'
RIFFCODEC['SFMC'] = 'CrystalNet Surface Fitting Method'
RIFFCODEC['SMSC'] = 'Radius SMSC'
RIFFCODEC['SMSD'] = 'Radius SMSD'
RIFFCODEC['smsv'] = 'WorldConnect Wavelet Video'
RIFFCODEC['SPIG'] = 'Radius Spigot'
RIFFCODEC['SPLC'] = 'Splash Studios ACM Audio Codec'
RIFFCODEC['SQZ2'] = 'Microsoft VXTreme Video Codec V2'
RIFFCODEC['STVA'] = 'ST CMOS Imager Data (Bayer)'
RIFFCODEC['STVB'] = 'ST CMOS Imager Data (Nudged Bayer)'
RIFFCODEC['STVC'] = 'ST CMOS Imager Data (Bunched)'
RIFFCODEC['STVX'] = 'ST CMOS Imager Data (Extended CODEC Data Format)'
RIFFCODEC['STVY'] = 'ST CMOS Imager Data (Extended CODEC Data Format with Correction Data)'
RIFFCODEC['SV10'] = 'Sorenson Video R1'
RIFFCODEC['SVQ1'] = 'Sorenson Video'
RIFFCODEC['SVQ1'] = 'Sorenson Video R3'
RIFFCODEC['TLMS'] = 'TeraLogic Motion Intraframe Codec (TLMS)'
RIFFCODEC['TLST'] = 'TeraLogic Motion Intraframe Codec (TLST)'
RIFFCODEC['TM20'] = 'Duck TrueMotion 2.0'
RIFFCODEC['TM2X'] = 'Duck TrueMotion 2X'
RIFFCODEC['TMIC'] = 'TeraLogic Motion Intraframe Codec (TMIC)'
RIFFCODEC['TMOT'] = 'Horizons Technology TrueMotion S'
RIFFCODEC['tmot'] = 'Horizons TrueMotion Video Compression'
RIFFCODEC['TR20'] = 'Duck TrueMotion RealTime 2.0'
RIFFCODEC['TSCC'] = 'TechSmith Screen Capture Codec'
RIFFCODEC['TV10'] = 'Tecomac Low-Bit Rate Codec'
RIFFCODEC['TY0N'] = 'Trident ?TY0N?'
RIFFCODEC['TY2C'] = 'Trident ?TY2C?'
RIFFCODEC['TY2N'] = 'Trident ?TY2N?'
RIFFCODEC['UCOD'] = 'eMajix.com ClearVideo'
RIFFCODEC['ULTI'] = 'IBM Ultimotion'
RIFFCODEC['UYVY'] = 'UYVY 4:2:2 byte ordering'
RIFFCODEC['V261'] = 'Lucent VX2000S'
RIFFCODEC['V422'] = '24 bit YUV 4:2:2 Format'
RIFFCODEC['V655'] = '16 bit YUV 4:2:2 Format'
RIFFCODEC['VCR1'] = 'ATI VCR 1.0'
RIFFCODEC['VCR2'] = 'ATI VCR 2.0'
RIFFCODEC['VCR3'] = 'ATI VCR 3.0'
RIFFCODEC['VCR4'] = 'ATI VCR 4.0'
RIFFCODEC['VCR5'] = 'ATI VCR 5.0'
RIFFCODEC['VCR6'] = 'ATI VCR 6.0'
RIFFCODEC['VCR7'] = 'ATI VCR 7.0'
RIFFCODEC['VCR8'] = 'ATI VCR 8.0'
RIFFCODEC['VCR9'] = 'ATI VCR 9.0'
RIFFCODEC['VDCT'] = 'Video Maker Pro DIB'
RIFFCODEC['VDOM'] = 'VDOnet VDOWave'
RIFFCODEC['VDOW'] = 'VDOnet VDOLive (H.263)'
RIFFCODEC['VDTZ'] = 'Darim Vison VideoTizer YUV'
RIFFCODEC['VGPX'] = 'VGPixel Codec'
RIFFCODEC['VIDS'] = 'Vitec Multimedia YUV 4:2:2 CCIR 601 for V422'
RIFFCODEC['VIDS'] = 'YUV 4:2:2 CCIR 601 for V422'
RIFFCODEC['VIFP'] = '?VIFP?'
RIFFCODEC['VIVO'] = 'Vivo H.263 v2.00'
RIFFCODEC['vivo'] = 'Vivo H.263'
RIFFCODEC['VIXL'] = 'Miro Video XL'
RIFFCODEC['VLV1'] = 'Videologic VLCAP.DRV'
RIFFCODEC['VP30'] = 'On2 VP3.0'
RIFFCODEC['VP31'] = 'On2 VP3.1'
RIFFCODEC['VX1K'] = 'VX1000S Video Codec'
RIFFCODEC['VX2K'] = 'VX2000S Video Codec'
RIFFCODEC['VXSP'] = 'VX1000SP Video Codec'
RIFFCODEC['WBVC'] = 'Winbond W9960'
RIFFCODEC['WHAM'] = 'Microsoft Video 1 (WHAM)'
RIFFCODEC['WINX'] = 'Winnov Software Compression'
RIFFCODEC['WJPG'] = 'AverMedia Winbond JPEG'
RIFFCODEC['WMV1'] = 'Windows Media Video V7'
RIFFCODEC['WMV2'] = 'Windows Media Video V8'
RIFFCODEC['WMV3'] = 'Windows Media Video V9'
RIFFCODEC['WNV1'] = 'Winnov Hardware Compression'
RIFFCODEC['x263'] = 'Xirlink H.263'
RIFFCODEC['XLV0'] = 'NetXL Video Decoder'
RIFFCODEC['XMPG'] = 'Xing MPEG (I-Frame only)'
RIFFCODEC['XVID'] = 'XviD MPEG-4'
RIFFCODEC['XXAN'] = '?XXAN?'
RIFFCODEC['Y211'] = 'YUV 2:1:1 Packed'
RIFFCODEC['Y411'] = 'YUV 4:1:1 Packed'
RIFFCODEC['Y41B'] = 'YUV 4:1:1 Planar'
RIFFCODEC['Y41P'] = 'PC1 4:1:1'
RIFFCODEC['Y41T'] = 'PC1 4:1:1 with transparency'
RIFFCODEC['Y42B'] = 'YUV 4:2:2 Planar'
RIFFCODEC['Y42T'] = 'PCI 4:2:2 with transparency'
RIFFCODEC['Y8  '] = 'Grayscale video'
RIFFCODEC['YC12'] = 'Intel YUV 12 codec'
RIFFCODEC['YC12'] = 'Intel YUV12 Codec'
RIFFCODEC['YUV8'] = 'Winnov Caviar YUV8'
RIFFCODEC['YUV9'] = 'Intel YUV9'
RIFFCODEC['YUY2'] = 'Uncompressed YUV 4:2:2'
RIFFCODEC['YUYV'] = 'Canopus YUV'
RIFFCODEC['YV12'] = 'YVU12 Planar'
RIFFCODEC['YVU9'] = 'Intel YVU9 Planar'
RIFFCODEC['YVYU'] = 'YVYU 4:2:2 byte ordering'
RIFFCODEC['ZLIB'] = '?ZLIB?'
RIFFCODEC['ZPEG'] = 'Metheus Video Zipper'

