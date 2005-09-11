# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# freq.py - Video Channel Frequencies
# -----------------------------------------------------------------------
# $Id$
#
# Notes: http://ivtv.sf.net
#
# Todo:        
#
# -----------------------------------------------------------------------------
# kaa-record - A recording module
# Copyright (C) 2005 S<F6>nke Schwardt, Dirk Meyer
#
# First Edition: Rob Shortt <rob@tvcentric.com>
# Maintainer:    Rob Shortt <rob@tvcentric.com>
#
# Please see the file doc/CREDITS for a complete list of authors.
#
# -----------------------------------------------------------------------
#
# The contents of this file are originally taken from:
#
#   Freevo - A Home Theater PC framework
#   Copyright (C) 2003-2005 Krister Lagerstrom, Dirk Meyer, et al. 
#   Please see Freevo's doc/CREDITS for a complete list of authors.
#   src/tv/freq.py by Thomas Schueppel <stain@cs.tu-berlin.de>,
#                     Rob Shortt <rob@tvcentric.com>
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
# ----------------------------------------------------------------------- */

import logging
import config

log = logging.getLogger('tv')

def get_frequency(tuner_id, chanlist=None):
    """
    Returns the frequency of a channel in MHz
    """
    tuner_id = str(tuner_id)
    freq = config.FREQUENCY_TABLE.get(tuner_id) 	 

    if freq: 	 
        log.debug('USING CUSTOM FREQUENCY: chan="%s", freq="%s"' % (tuner_id, freq))
    else: 	 
        if not chanlist:
            chanlist = config.CONF.chanlist

        freq_table = CHANLIST.get(chanlist) 	 
        if freq_table: 	 
            freq = freq_table.get(tuner_id) 	 
            if not freq: 	 
                print String(_('ERROR')+': ' + \
                      (_('Unable to get frequency for %s from %s.') % \
                      (tuner_id, chanlist))) 	 
                return 0 	 
        else: 	 
            print String(_('ERROR')+': ' + \
                 (_('Unable to get frequency table for %s.') % chanlist)) 	 
            return 0 	 

        log.debug('USING STANDARD FREQUENCY: chan="%s", freq="%s"' % \
                  (tuner_id, freq)) 	 

    return freq


def get_frequency_khz(tuner_id, chanlist=None):
    """
    Returns the frequency of a channel in KHz
    """
    return float(get_frequency(tuner_id, chanlist))/1000.00


NTSC_BCAST = [
     ("2",	 55250),
     ("3",	 61250),
     ("4",	 67250),
     ("5",	 77250),
     ("6",	 83250),
     ("7",	175250),
     ("8",	181250),
     ("9",	187250),
     ("10",	193250),
     ("11",	199250),
     ("12",	205250),
     ("13",	211250),
     ("14",	471250),
     ("15",	477250),
     ("16",	483250),
     ("17",	489250),
     ("18",	495250),
     ("19",	501250),
     ("20",	507250),
     ("21",	513250),
     ("22",	519250),
     ("23",	525250),
     ("24",	531250),
     ("25",	537250),
     ("26",	543250),
     ("27",	549250),
     ("28",	555250),
     ("29",	561250),
     ("30",	567250),
     ("31",	573250),
     ("32",	579250),
     ("33",	585250),
     ("34",	591250),
     ("35",	597250),
     ("36",	603250),
     ("37",	609250),
     ("38",	615250),
     ("39",	621250),
     ("40",	627250),
     ("41",	633250),
     ("42",	639250),
     ("43",	645250),
     ("44",	651250),
     ("45",	657250),
     ("46",	663250),
     ("47",	669250),
     ("48",	675250),
     ("49",	681250),
     ("50",	687250),
     ("51",	693250),
     ("52",	699250),
     ("53",	705250),
     ("54",	711250),
     ("55",	717250),
     ("56",	723250),
     ("57",	729250),
     ("58",	735250),
     ("59",	741250),
     ("60",	747250),
     ("61",	753250),
     ("62",	759250),
     ("63",	765250),
     ("64",	771250),
     ("65",	777250),
     ("66",	783250),
     ("67",	789250),
     ("68",	795250),
     ("69",	801250),
     ("70",	807250),
     ("71",	813250),
     ("72",	819250),
     ("73",	825250),
     ("74",	831250),
     ("75",	837250),
     ("76",	843250),
     ("77",	849250),
     ("78",	855250),
     ("79",	861250),
     ("80",	867250),
     ("81",	873250),
     ("82",	879250),
     ("83",	885250),
]

NTSC_CABLE = [
     ("1",	 73250),
     ("2",	 55250),
     ("3",	 61250),
     ("4",	 67250),
     ("5",	 77250),
     ("6",	 83250),
     ("7",	175250),
     ("8",	181250),
     ("9",	187250),
     ("10",	193250),
     ("11",	199250),
     ("12",	205250),
     ("13",	211250),
     ("14",	121250),
     ("15",	127250),
     ("16",	133250),
     ("17",	139250),
     ("18",	145250),
     ("19",	151250),
     ("20",	157250),
     ("21",	163250),
     ("22",	169250),
     ("23",	217250),
     ("24",	223250),
     ("25",	229250),
     ("26",	235250),
     ("27",	241250),
     ("28",	247250),
     ("29",	253250),
     ("30",	259250),
     ("31",	265250),
     ("32",	271250),
     ("33",	277250),
     ("34",	283250),
     ("35",	289250),
     ("36",	295250),
     ("37",	301250),
     ("38",	307250),
     ("39",	313250),
     ("40",	319250),
     ("41",	325250),
     ("42",	331250),
     ("43",	337250),
     ("44",	343250),
     ("45",	349250),
     ("46",	355250),
     ("47",	361250),
     ("48",	367250),
     ("49",	373250),
     ("50",	379250),
     ("51",	385250),
     ("52",	391250),
     ("53",	397250),
     ("54",	403250),
     ("55",	409250),
     ("56",	415250),
     ("57",	421250),
     ("58",	427250),
     ("59",	433250),
     ("60",	439250),
     ("61",	445250),
     ("62",	451250),
     ("63",	457250),
     ("64",	463250),
     ("65",	469250),
     ("66",	475250),
     ("67",	481250),
     ("68",	487250),
     ("69",	493250),
     ("70",	499250),
     ("71",	505250),
     ("72",	511250),
     ("73",	517250),
     ("74",	523250),
     ("75",	529250),
     ("76",	535250),
     ("77",	541250),
     ("78",	547250),
     ("79",	553250),
     ("80",	559250),
     ("81",	565250),
     ("82",	571250),
     ("83",	577250),
     ("84",	583250),
     ("85",	589250),
     ("86",	595250),
     ("87",	601250),
     ("88",	607250),
     ("89",	613250),
     ("90",	619250),
     ("91",	625250),
     ("92",	631250),
     ("93",	637250),
     ("94",	643250),
     ("95",	 91250),
     ("96",	 97250),
     ("97",	103250),
     ("98",	109250),
     ("99",	115250),
     ("100",	649250),
     ("101",	655250),
     ("102",	661250),
     ("103",	667250),
     ("104",	673250),
     ("105",	679250),
     ("106",	685250),
     ("107",	691250),
     ("108",	697250),
     ("109",	703250),
     ("110",	709250),
     ("111",	715250),
     ("112",	721250),
     ("113",	727250),
     ("114",	733250),
     ("115",	739250),
     ("116",	745250),
     ("117",	751250),
     ("118",	757250),
     ("119",	763250),
     ("120",	769250),
     ("121",	775250),
     ("122",	781250),
     ("123",	787250),
     ("124",	793250),
     ("125",	799250),
     ("T7", 	  8250),
     ("T8",	 14250),
     ("T9",	 20250),
     ("T10",	 26250),
     ("T11",	 32250),
     ("T12",	 38250),
     ("T13",	 44250),
     ("T14",	 50250),
]

NTSC_HRC = [
     ("1",	  72000),
     ("2",	  54000),
     ("3",	  60000),
     ("4",	  66000),
     ("5",	  78000),
     ("6",	  84000),
     ("7",	 174000),
     ("8",	 180000),
     ("9",	 186000),
     ("10",	 192000),
     ("11",	 198000),
     ("12",	 204000),
     ("13",	 210000),
     ("14",	 120000),
     ("15",	 126000),
     ("16",	 132000),
     ("17",	 138000),
     ("18",	 144000),
     ("19",	 150000),
     ("20",	 156000),
     ("21",	 162000),
     ("22",	 168000),
     ("23",	 216000),
     ("24",	 222000),
     ("25",	 228000),
     ("26",	 234000),
     ("27",	 240000),
     ("28",	 246000),
     ("29",	 252000),
     ("30",	 258000),
     ("31",	 264000),
     ("32",	 270000),
     ("33",	 276000),
     ("34",	 282000),
     ("35",	 288000),
     ("36",	 294000),
     ("37",	 300000),
     ("38",	 306000),
     ("39",	 312000),
     ("40",	 318000),
     ("41",	 324000),
     ("42",	 330000),
     ("43",	 336000),
     ("44",	 342000),
     ("45",	 348000),
     ("46",	 354000),
     ("47",	 360000),
     ("48",	 366000),
     ("49",	 372000),
     ("50",	 378000),
     ("51",	 384000),
     ("52",	 390000),
     ("53",	 396000),
     ("54",	 402000),
     ("55",	 408000),
     ("56",	 414000),
     ("57",	 420000),
     ("58",	 426000),
     ("59",	 432000),
     ("60",	 438000),
     ("61",	 444000),
     ("62",	 450000),
     ("63",	 456000),
     ("64",	 462000),
     ("65",	 468000),
     ("66",	 474000),
     ("67",	 480000),
     ("68",	 486000),
     ("69",	 492000),
     ("70",	 498000),
     ("71",	 504000),
     ("72",	 510000),
     ("73",	 516000),
     ("74",	 522000),
     ("75",	 528000),
     ("76",	 534000),
     ("77",	 540000),
     ("78",	 546000),
     ("79",	 552000),
     ("80",	 558000),
     ("81",	 564000),
     ("82",	 570000),
     ("83",	 576000),
     ("84",	 582000),
     ("85",	 588000),
     ("86",	 594000),
     ("87",	 600000),
     ("88",	 606000),
     ("89",	 612000),
     ("90",	 618000),
     ("91",	 624000),
     ("92",	 630000),
     ("93",	 636000),
     ("94",	 642000),
     ("95",	 900000),
     ("96",	 960000),
     ("97",	 102000),
     ("98",	 108000),
     ("99",	 114000),
     ("100",	 648000),
     ("101",	 654000),
     ("102",	 660000),
     ("103",	 666000),
     ("104",	 672000),
     ("105",	 678000),
     ("106",	 684000),
     ("107",	 690000),
     ("108",	 696000),
     ("109",	 702000),
     ("110",	 708000),
     ("111",	 714000),
     ("112",	 720000),
     ("113",	 726000),
     ("114",	 732000),
     ("115",	 738000),
     ("116",	 744000),
     ("117",	 750000),
     ("118",	 756000),
     ("119",	 762000),
     ("120",	 768000),
     ("121",	 774000),
     ("122",	 780000),
     ("123",	 786000),
     ("124",	 792000),
     ("125",	 798000),
     ("T7",	   7000),
     ("T8",	  13000),
     ("T9",	  19000),
     ("T10",	  25000),
     ("T11",	  31000),
     ("T12",	  37000),
     ("T13",	  43000),
     ("T14",	  49000),
]

NTSC_BCAST_JP = [
     ("1",   91250),
     ("2",   97250),
     ("3",  103250),
     ("4",  171250),
     ("5",  177250),
     ("6",  183250),
     ("7",  189250),
     ("8",  193250),
     ("9",  199250),
     ("10", 205250),
     ("11", 211250),
     ("12", 217250),
     ("13", 471250),
     ("14", 477250),
     ("15", 483250),
     ("16", 489250),
     ("17", 495250),
     ("18", 501250),
     ("19", 507250),
     ("20", 513250),
     ("21", 519250),
     ("22", 525250),
     ("23", 531250),
     ("24", 537250),
     ("25", 543250),
     ("26", 549250),
     ("27", 555250),
     ("28", 561250),
     ("29", 567250),
     ("30", 573250),
     ("31", 579250),
     ("32", 585250),
     ("33", 591250),
     ("34", 597250),
     ("35", 603250),
     ("36", 609250),
     ("37", 615250),
     ("38", 621250),
     ("39", 627250),
     ("40", 633250),
     ("41", 639250),
     ("42", 645250),
     ("43", 651250),
     ("44", 657250),
     ("45", 663250),
     ("46", 669250),
     ("47", 675250),
     ("48", 681250),
     ("49", 687250),
     ("50", 693250),
     ("51", 699250),
     ("52", 705250),
     ("53", 711250),
     ("54", 717250),
     ("55", 723250),
     ("56", 729250),
     ("57", 735250),
     ("58", 741250),
     ("59", 747250),
     ("60", 753250),
     ("61", 759250),
     ("62", 765250),
]

NTSC_CABLE_JP = [
     ("13",	109250),
     ("14",	115250),
     ("15",	121250),
     ("16",	127250),
     ("17",	133250),
     ("18",	139250),
     ("19",	145250),
     ("20",	151250),
     ("21",	157250),
     ("22",	165250),
     ("23",	223250),
     ("24",	231250),
     ("25",	237250),
     ("26",	243250),
     ("27",	249250),
     ("28",	253250),
     ("29",	259250),
     ("30",	265250),
     ("31",	271250),
     ("32",	277250),
     ("33",	283250),
     ("34",	289250),
     ("35",	295250),
     ("36",	301250),
     ("37",	307250),
     ("38",	313250),
     ("39",	319250),
     ("40",	325250),
     ("41",	331250),
     ("42",	337250),
     ("43",	343250),
     ("44",	349250),
     ("45", 	355250),
     ("46", 	361250),
     ("47", 	367250),
     ("48", 	373250),
     ("49", 	379250),
     ("50", 	385250),
     ("51", 	391250),
     ("52", 	397250),
     ("53", 	403250),
     ("54", 	409250),
     ("55", 	415250),
     ("56", 	421250),
     ("57", 	427250),
     ("58", 	433250),
     ("59", 	439250),
     ("60", 	445250),
     ("61", 	451250),
     ("62", 	457250),
     ("63",	463250),
]

NTSC_CABLE_CAN = [
    ( "2",	 61750 ),
    ( "3",	 67750 ),
    ( "4",	 73750 ),
    ( "5",	 83750 ),
    ( "6",	 89750 ),
    ( "7",	181750 ),
    ( "8",	187750 ),
    ( "9",	193750 ),
    ( "10",	199750 ),
    ( "11",	205750 ),
    ( "12",	211750 ),
    ( "13",	217750 ),
    ( "14",	127750 ),
    ( "15",	133750 ),
    ( "16",	139750 ),
    ( "17",	145750 ),
    ( "18",	151750 ),
    ( "19",	157750 ),
    ( "20",	163750 ),
    ( "21",	169750 ),
    ( "22",	175750 ),
    ( "23",	223750 ),
    ( "24",	229750 ),
    ( "25",	235750 ),
    ( "26",	241750 ),
    ( "27",	247750 ),
    ( "28",	253750 ),
    ( "29",	259750 ),
    ( "30",	265750 ),
    ( "31",	271750 ),
    ( "32",	277750 ),
    ( "33",	283750 ),
    ( "34",	289750 ),
    ( "35",	295750 ),
    ( "36",	301750 ),
    ( "37",	307750 ),
    ( "38",	313750 ),
    ( "39",	319750 ),
    ( "40",	325750 ),
    ( "41",	331750 ),
    ( "42",	337750 ),
    ( "43",	343750 ),
    ( "44",	349750 ),
    ( "45",	355750 ),
    ( "46",	361750 ),
    ( "47",	367750 ),
    ( "48",	373750 ),
    ( "49",	379750 ),
    ( "50",	385750 ),
    ( "51",	391750 ),
    ( "52",	397750 ),
    ( "53",	403750 ),
    ( "54",	409750 ),
    ( "55",	415750 ),
    ( "56",	421750 ),
    ( "57",	427750 ),
    ( "58",	433750 ),
    ( "59",	439750 ),
    ( "60",	445750 ),
    ( "61",	451750 ),
    ( "62",	457750 ),
    ( "63",	463750 ),
    ( "64",	469750 ),
    ( "65",	475750 ),
    ( "66",	481750 ),
    ( "67",	487750 ),
    ( "68",	493750 ),
    ( "69",	499750 ),
    ( "70",	505750 ),
    ( "71",	511750 ),
    ( "72",	517750 ),
    ( "73",	523750 ),
    ( "74",	529750 ),
    ( "75",	535750 ),
    ( "76",	541750 ),
    ( "77",	547750 ),
    ( "78",	553750 ),
    ( "79",	559750 ),
    ( "80",	565750 ),
    ( "81",	571750 ),
    ( "82",	577750 ),
    ( "83",	583750 ),
    ( "84",	589750 ),
    ( "85",	595750 ),
    ( "86",	601750 ),
    ( "87",	607750 ),
    ( "88",	613750 ),
    ( "89",	619750 ),
    ( "90",	625750 ),
    ( "91",	631750 ),
    ( "92",	637750 ),
    ( "93",	643750 ),
    ( "94",	649750 ),
    ( "95",	 97750 ),
    ( "96",	103750 ),
    ( "97",	109750 ),
    ( "98",	115750 ),
    ( "99",	121750 ),
    ( "100",	655750 ),
    ( "101",	661750 ),
    ( "102",	667750 ),
    ( "103",	673750 ),
    ( "104",	679750 ),
    ( "105",	685750 ),
    ( "106",	691750 ),
    ( "107",	697750 ),
    ( "108",	703750 ),
    ( "109",	709750 ),
    ( "110",	715750 ),
    ( "111",	721750 ),
    ( "112",	727750 ),
    ( "113",	733750 ),
    ( "114",	739750 ),
    ( "115",	745750 ),
    ( "116",	751750 ),
    ( "117",	757750 ),
    ( "118",	763750 ),
    ( "119",	769750 ),
    ( "120",	775750 ),
    ( "121",	781750 ),
    ( "122",	787750 ),
    ( "123",	793750 ),
    ( "124",	799750 ),
    ( "125",	805750 ),
]

PAL_AUSTRALIA = [
     ("0",	 46250),
     ("1",	 57250),
     ("2",	 64250),
     ("3",	 86250),
     ("4",  	 95250),
     ("5",  	102250),
     ("6",  	175250),
     ("7",  	182250),
     ("8",  	189250),
     ("9",  	196250),
     ("10", 	209250),
     ("11",	216250),
     ("28",	527250),
     ("29",	534250),
     ("30",	541250),
     ("31",	548250),
     ("32",	555250),
     ("33",	562250),
     ("34",	569250),
     ("35",	576250),
     ("39",	604250),
     ("40",	611250),
     ("41",	618250),
     ("42",	625250),
     ("43",	632250),
     ("44",	639250),
     ("45",	646250),
     ("46",	653250),
     ("47",	660250),
     ("48",	667250),
     ("49",	674250),
     ("50",	681250),
     ("51",	688250),
     ("52",	695250),
     ("53",	702250),
     ("54",	709250),
     ("55",	716250),
     ("56",	723250),
     ("57",	730250),
     ("58",	737250),
     ("59",	744250),
     ("60",	751250),
     ("61",	758250),
     ("62",	765250),
     ("63",	772250),
     ("64",	779250),
     ("65",	786250),
     ("66",	793250),
     ("67",	800250),
     ("68",	807250),
     ("69",	814250),
]

FREQ_CCIR_I_III = [
     ("E2",	  48250),
     ("E3",	  55250),
     ("E4",	  62250),
     ("S01",	  69250),
     ("S02",	  76250),
     ("S03",	  83250),
     ("E5",	 175250),
     ("E6",	 182250),
     ("E7",	 189250),
     ("E8",	 196250),
     ("E9",	 203250),
     ("E10",	 210250),
     ("E11",	 217250),
     ("E12",	 224250),
]

FREQ_CCIR_SL_SH = [
     ("SE1",	 105250),
     ("SE2",	 112250),
     ("SE3",	 119250),
     ("SE4",	 126250),
     ("SE5",	 133250),
     ("SE6",	 140250),
     ("SE7",	 147250),
     ("SE8",	 154250),
     ("SE9",	 161250),
     ("SE10",    168250),
     ("SE11",    231250),
     ("SE12",    238250),
     ("SE13",    245250),
     ("SE14",    252250),
     ("SE15",    259250),
     ("SE16",    266250),
     ("SE17",    273250),
     ("SE18",    280250),
     ("SE19",    287250),
     ("SE20",    294250),
]

FREQ_CCIR_H = [
     ("S21", 303250),
     ("S22", 311250),
     ("S23", 319250),
     ("S24", 327250),
     ("S25", 335250),
     ("S26", 343250),
     ("S27", 351250),
     ("S28", 359250),
     ("S29", 367250),
     ("S30", 375250),
     ("S31", 383250),
     ("S32", 391250),
     ("S33", 399250),
     ("S34", 407250),
     ("S35", 415250),
     ("S36", 423250),
     ("S37", 431250),
     ("S38", 439250),
     ("S39", 447250),
     ("S40", 455250),
     ("S41", 463250),
]

FREQ_OIRT_I_III = [
     ("R1",       49750),
     ("R2",       59250),
     ("R3",       77250),
     ("R4",       84250),
     ("R5",       93250),
     ("R6",	 175250),
     ("R7",	 183250),
     ("R8",	 191250),
     ("R9",	 199250),
     ("R10",	 207250),
     ("R11",	 215250),
     ("R12",	 223250),
]

FREQ_OIRT_SL_SH = [
     ("SR1",	 111250),
     ("SR2",	 119250),
     ("SR3",	 127250),
     ("SR4",	 135250),
     ("SR5",	 143250),
     ("SR6",	 151250),
     ("SR7",	 159250),
     ("SR8",	 167250),
     ("SR11",    231250),
     ("SR12",    239250),
     ("SR13",    247250),
     ("SR14",    255250),
     ("SR15",    263250),
     ("SR16",    271250),
     ("SR17",    279250),
     ("SR18",    287250),
     ("SR19",    295250),
]

FREQ_UHF = [
     ("21",  471250),
     ("22",  479250),
     ("23",  487250),
     ("24",  495250),
     ("25",  503250),
     ("26",  511250),
     ("27",  519250),
     ("28",  527250),
     ("29",  535250),
     ("30",  543250),
     ("31",  551250),
     ("32",  559250),
     ("33",  567250),
     ("34",  575250),
     ("35",  583250),
     ("36",  591250),
     ("37",  599250),
     ("38",  607250),
     ("39",  615250),
     ("40",  623250),
     ("41",  631250),
     ("42",  639250),
     ("43",  647250),
     ("44",  655250),
     ("45",  663250),
     ("46",  671250),
     ("47",  679250),
     ("48",  687250),
     ("49",  695250),
     ("50",  703250),
     ("51",  711250),
     ("52",  719250),
     ("53",  727250),
     ("54",  735250),
     ("55",  743250),
     ("56",  751250),
     ("57",  759250),
     ("58",  767250),
     ("59",  775250),
     ("60",  783250),
     ("61",  791250),
     ("62",  799250),
     ("63",  807250),
     ("64",  815250),
     ("65",  823250),
     ("66",  831250),
     ("67",  839250),
     ("68",  847250),
     ("69",  855250),
]

PAL_EUROPE = FREQ_CCIR_I_III + FREQ_CCIR_SL_SH + FREQ_CCIR_H + FREQ_UHF


PAL_EUROPE_EAST =  FREQ_OIRT_I_III + FREQ_OIRT_SL_SH + FREQ_CCIR_H + FREQ_UHF


PAL_ITALY = [
     ("2",	 53750),
     ("3",	 62250),
     ("4",	 82250),
     ("5",	175250),
     ("6",	183750),
     ("7",	192250),
     ("8",	201250),
     ("9",	210250),
     ("10",	210250),
     ("11",	217250),
     ("12",	224250),
] + FREQ_UHF

PAL_IRELAND = [
    ( "A0",    45750 ),
    ( "A1",    48000 ),
    ( "A2",    53750 ),
    ( "A3",    56000 ),
    ( "A4",    61750 ),
    ( "A5",    64000 ),
    ( "A6",   175250 ),
    ( "A7",   176000 ),
    ( "A8",   183250 ),
    ( "A9",   184000 ),
    ( "A10",   191250 ),
    ( "A11",   192000 ),
    ( "A12",   199250 ),
    ( "A13",   200000 ),
    ( "A14",   207250 ),
    ( "A15",   208000 ),
    ( "A16",   215250 ),
    ( "A17",   216000 ),
    ( "A18",   224000 ),
    ( "A19",   232000 ),
    ( "A20",   248000 ),
    ( "A21",   256000 ),
    ( "A22",   264000 ),
    ( "A23",   272000 ),
    ( "A24",   280000 ),
    ( "A25",   288000 ),
    ( "A26",   296000 ),
    ( "A27",   304000 ),
    ( "A28",   312000 ),
    ( "A29",   320000 ),
    ( "A30",   344000 ),
    ( "A31",   352000 ),
    ( "A32",   408000 ),
    ( "A33",   416000 ),
    ( "A34",   448000 ),
    ( "A35",   480000 ),
    ( "A36",   520000 ),
] + FREQ_UHF


PAL_NEWZEALAND = [
     ("1", 	  45250),
     ("2",	  55250),
     ("3",	  62250),
     ("4",	 175250),
     ("5",	 182250),
     ("5A",	 138250),
     ("6",	 189250),
     ("7",	 196250),
     ("8",	 203250),
     ("9",	 210250),
     ("10",	 217250),
]

SECAM_FRANCE = [
    ( "K01",    47750 ),
    ( "K02",    55750 ),
    ( "K03",    60500 ),
    ( "K04",    63750 ),
    ( "K05",   176000 ),
    ( "K06",   184000 ),
    ( "K07",   192000 ),
    ( "K08",   200000 ),
    ( "K09",   208000 ),
    ( "K10",   216000 ),
    ( "KB",    116750 ),
    ( "KC",    128750 ),
    ( "KD",    140750 ),
    ( "KE",    159750 ),
    ( "KF",    164750 ),
    ( "KG",    176750 ),
    ( "KH",    188750 ),
    ( "KI",    200750 ),
    ( "KJ",    212750 ),
    ( "KK",    224750 ),
    ( "KL",    236750 ),
    ( "KM",    248750 ),
    ( "KN",    260750 ),
    ( "KO",    272750 ),
    ( "KP",    284750 ),
    ( "KQ",    296750 ),
    ( "H01",   303250 ),
    ( "H02",   311250 ),
    ( "H03",   319250 ),
    ( "H04",   327250 ),
    ( "H05",   335250 ),
    ( "H06",   343250 ),
    ( "H07",   351250 ),
    ( "H08",   359250 ),
    ( "H09",   367250 ),
    ( "H10",   375250 ),
    ( "H11",   383250 ),
    ( "H12",   391250 ),
    ( "H13",   399250 ),
    ( "H14",   407250 ),
    ( "H15",   415250 ),
    ( "H16",   423250 ),
    ( "H17",   431250 ),
    ( "H18",   439250 ),
    ( "H19",   447250 ),
] + FREQ_UHF

PAL_CHINA = [
    ( "1",	49750 ),
    ( "2",	57750 ),
    ( "3",	65750 ),
    ( "4",	77250 ),
    ( "5",	85250 ),
    ( "6",	112250 ),
    ( "7",	120250 ),
    ( "8",	128250 ),
    ( "9",	136250 ),
    ( "10",	144250 ),
    ( "11",	152250 ),
    ( "12",	160250 ),
    ( "13",	168250 ),
    ( "14",	176250 ),
    ( "15",	184250 ),
    ( "16",	192250 ),
    ( "17",	200250 ),
    ( "18",	208250 ),
    ( "19",	216250 ),
    ( "20",	224250 ),
    ( "21",	232250 ),
    ( "22",	240250 ),
    ( "23",	248250 ),
    ( "24",	256250 ),
    ( "25",	264250 ),
    ( "26",	272250 ),
    ( "27",	280250 ),
    ( "28",	288250 ),
    ( "29",	296250 ),
    ( "30",	304250 ),
    ( "31",	312250 ),
    ( "32",	320250 ),
    ( "33",	328250 ),
    ( "34",	336250 ),
    ( "35",	344250 ),
    ( "36",	352250 ),
    ( "37",	360250 ),
    ( "38",	368250 ),
    ( "39",	376250 ),
    ( "40",	384250 ),
    ( "41",	392250 ),
    ( "42",	400250 ),
    ( "43",	408250 ),
    ( "44",	416250 ),
    ( "45",	424250 ),
    ( "46",	432250 ),
    ( "47",	440250 ),
    ( "48",	448250 ),
    ( "49",	456250 ),
    ( "50",	463250 ),
    ( "51",	471250 ),
    ( "52",	479250 ),
    ( "53",	487250 ),
    ( "54",	495250 ),
    ( "55",	503250 ),
    ( "56",	511250 ),
    ( "57",	519250 ),
    ( "58",	527250 ),
    ( "59",	535250 ),
    ( "60",	543250 ),
    ( "61",	551250 ),
    ( "62",	559250 ),
    ( "63",	607250 ),
    ( "64",	615250 ),
    ( "65",	623250 ),
    ( "66",	631250 ),
    ( "67",	639250 ),
    ( "68",	647250 ),
    ( "69",	655250 ),
    ( "70",	663250 ),
    ( "71",	671250 ),
    ( "72",	679250 ),
    ( "73",	687250 ),
    ( "74",	695250 ),
    ( "75",	703250 ),
    ( "76",	711250 ),
    ( "77",	719250 ),
    ( "78",	727250 ),
    ( "79",	735250 ),
    ( "80",	743250 ),
    ( "81",	751250 ),
    ( "82",	759250 ),
    ( "83",	767250 ),
    ( "84",	775250 ),
    ( "85",	783250 ),
    ( "86",	791250 ),
    ( "87",	799250 ),
    ( "88",	807250 ),
    ( "89",	815250 ),
    ( "90",	823250 ),
    ( "91",	831250 ),
    ( "92",	839250 ),
    ( "93",	847250 ),
    ( "94",	855250 ),
]

PAL_BCAST_ZA = [
    ( "1", 175250 ),
    ( "2", 183250 ),
    ( "3", 191250 ),
    ( "4", 199250 ),
    ( "5", 207250 ),
    ( "6", 215250 ),
    ( "7", 223250 ),
    ( "8", 231250 ),
] + FREQ_UHF

ARGENTINA = [
    ( "001",   56250 ),
    ( "002",   62250 ),
    ( "003",   68250 ),
    ( "004",   78250 ),
    ( "005",   84250 ),
    ( "006",  176250 ),
    ( "007",  182250 ),
    ( "008",  188250 ),
    ( "009",  194250 ),
    ( "010",  200250 ),
    ( "011",  206250 ),
    ( "012",  212250 ),
    ( "013",  122250 ),
    ( "014",  128250 ),
    ( "015",  134250 ),
    ( "016",  140250 ),
    ( "017",  146250 ),
    ( "018",  152250 ),
    ( "019",  158250 ),
    ( "020",  164250 ),
    ( "021",  170250 ),
    ( "022",  218250 ),
    ( "023",  224250 ),
    ( "024",  230250 ),
    ( "025",  236250 ),
    ( "026",  242250 ),
    ( "027",  248250 ),
    ( "028",  254250 ),
    ( "029",  260250 ),
    ( "030",  266250 ),
    ( "031",  272250 ),
    ( "032",  278250 ),
    ( "033",  284250 ),
    ( "034",  290250 ),
    ( "035",  296250 ),
    ( "036",  302250 ),
    ( "037",  308250 ),
    ( "038",  314250 ),
    ( "039",  320250 ),
    ( "040",  326250 ),
    ( "041",  332250 ),
    ( "042",  338250 ),
    ( "043",  344250 ),
    ( "044",  350250 ),
    ( "045",  356250 ),
    ( "046",  362250 ),
    ( "047",  368250 ),
    ( "048",  374250 ),
    ( "049",  380250 ),
    ( "050",  386250 ),
    ( "051",  392250 ),
    ( "052",  398250 ),
    ( "053",  404250 ),
    ( "054",  410250 ),
    ( "055",  416250 ),
    ( "056",  422250 ),
    ( "057",  428250 ),
    ( "058",  434250 ),
    ( "059",  440250 ),
    ( "060",  446250 ),
    ( "061",  452250 ),
    ( "062",  458250 ),
    ( "063",  464250 ),
    ( "064",  470250 ),
    ( "065",  476250 ),
    ( "066",  482250 ),
    ( "067",  488250 ),
    ( "068",  494250 ),
    ( "069",  500250 ),
    ( "070",  506250 ),
    ( "071",  512250 ),
    ( "072",  518250 ),
    ( "073",  524250 ),
    ( "074",  530250 ),
    ( "075",  536250 ),
    ( "076",  542250 ),
    ( "077",  548250 ),
    ( "078",  554250 ),
    ( "079",  560250 ),
    ( "080",  566250 ),
    ( "081",  572250 ),
    ( "082",  578250 ),
    ( "083",  584250 ),
    ( "084",  590250 ),
    ( "085",  596250 ),
    ( "086",  602250 ),
    ( "087",  608250 ),
    ( "088",  614250 ),
    ( "089",  620250 ),
    ( "090",  626250 ),
    ( "091",  632250 ),
    ( "092",  638250 ),
    ( "093",  644250 ),
]

RUSSIA= [
    ("R1",     49750 ),
    ("R2",     59250 ),
    ("R3",     77250 ),
    ("R4",     85250 ),
    ("R5",     93250 ),
    ("SR1",   111250 ),
    ("SR2",   119250 ),
    ("SR3",   127250 ),
    ("SR4",   135250 ),
    ("SR5",   143250 ),
    ("SR6",   151250 ),
    ("SR7",   159250 ),
    ("SR8",   167250 ),
    ("R6",     175250 ),
    ("R7",     183250 ),
    ("R8",     191250 ),
    ("R9",     199250 ),
    ("R10",    207250 ),
    ("R11",    215250 ),
    ("R12",    223250 ),
    ("SR11",  231250 ),
    ("SR12",  239250 ),
    ("SR13",  247250 ),
    ("SR14",  255250 ),
    ("SR15",  263250 ),
    ("SR16",  271250 ),
    ("SR17",  279250 ),
    ("SR18",  287250 ),
    ("SR19",   295250 ),
    ("SR20",   303250 ),
    ("SR21",   311250 ),
    ("SR22",   319250 ),
    ("SR23",   327250 ),
    ("SR24",   335250 ),
    ("SR25",   343250 ),
    ("SR26",   351250 ),
    ("SR27",   359250 ),
    ("SR28",   367250 ),
    ("SR29",   375250 ),
    ("SR30",   383250 ),
    ("SR31",   391250 ),
    ("SR32",   399250 ),
    ("SR33",   407250 ),
    ("SR34",   415250 ),
    ("SR35",   423250 ),
    ("SR36",   431250 ),
    ("SR37",   439250 ),
    ("SR38",   447250 ),
    ("SR39",   455250 ),
    ("SR40",   463250 ),
    ("21",    471250 ),
    ("22",    479250 ),
    ("23",    487250 ),
    ("24",    495250 ),
    ("25",    503250 ),
    ("26",    511250 ),
    ("27",    519250 ),
    ("28",    527250 ),
    ("29",    535250 ),
    ("30",    543250 ),
    ("31",    551250 ),
    ("32",    559250 ),
    ("33",    567250 ),
    ("34",    575250 ),
    ("35",    583250 ),
    ("36",    591250 ),
    ("37",    599250 ),
    ("38",    607250 ),
    ("39",    615250 ),
    ("40",    623250 ),
    ("41",    631250 ),
    ("42",    639250 ),
    ("43",    647250 ),
    ("44",    655250 ),
    ("45",    663250 ),
    ("46",    671250 ),
    ("47",    679250 ),
    ("48",    687250 ),
    ("49",    695250 ),
    ("50",    703250 ),
    ("51",    711250 ),
    ("52",    719250 ),
    ("53",    727250 ),
    ("54",    735250 ),
    ("55",    743250 ),
    ("56",    751250 ),
    ("57",    759250 ),
    ("58",    767250 ),
    ("59",    775250 ),
    ("60",    783250 ),
    ("61",    791250 ),
    ("62",    799250 ),
    ("63",    807250 ),
    ("64",    815250 ),
    ("65",    523250 ),
    ("66",    831250 ),
    ("67",    839250 ),
    ("68",    847250 ),
    ("69",    855250 ),
]

CHANLIST = {
     "us-bcast"         : dict(NTSC_BCAST),
     "us-cable"         : dict(NTSC_CABLE),
     "us-cable-hrc"     : dict(NTSC_HRC),
     "japan-bcast"      : dict(NTSC_BCAST_JP),
     "japan-cable"      : dict(NTSC_CABLE_JP),
     "europe-west"      : dict(PAL_EUROPE),
     "europe-east"      : dict(PAL_EUROPE_EAST),
     "italy"	        : dict(PAL_ITALY),
     "newzealand"       : dict(PAL_NEWZEALAND),
     "australia"        : dict(PAL_AUSTRALIA),
     "ireland"          : dict(PAL_IRELAND),
     "france"	        : dict(SECAM_FRANCE),
     "china-bcast"      : dict(PAL_CHINA),
     "canada-cable"     : dict(NTSC_CABLE_CAN),
     "southafrica"      : dict(PAL_BCAST_ZA),
     "argentina"        : dict(ARGENTINA),
     "russia"           : dict(RUSSIA),
}
