/*
 * frontend.h
 *
 * Copyright (C) 2000 Marcus Metzler <marcus@convergence.de>
 *                    Ralph  Metzler <ralph@convergence.de>
 *                    Holger Waechtler <holger@convergence.de>
 *                    Andre Draszik <ad@convergence.de>
 *                    for convergence integrated media GmbH
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public License
 * as published by the Free Software Foundation; either version 2.1
 * of the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
 *
 */

#ifndef _FRONTEND_H_
#define _FRONTEND_H_

#ifdef __KERNEL__
#include <linux/types.h>
#else
#if HAVE_INTTYPE_H
#include <inttypes.h>
#else
#if HAVE_STDINT_H
#include <stdint.h>
#endif
#endif
#endif


typedef enum {
        FE_QPSK,
        FE_QAM,
        FE_OFDM,
	FE_ATSC
} fe_type_t;


typedef enum {
	FE_IS_STUPID                  = 0,
	FE_CAN_INVERSION_AUTO         = 0x1,
	FE_CAN_FEC_1_2                = 0x2,
	FE_CAN_FEC_2_3                = 0x4,
	FE_CAN_FEC_3_4                = 0x8,
	FE_CAN_FEC_4_5                = 0x10,
	FE_CAN_FEC_5_6                = 0x20,
	FE_CAN_FEC_6_7                = 0x40,
	FE_CAN_FEC_7_8                = 0x80,
	FE_CAN_FEC_8_9                = 0x100,
	FE_CAN_FEC_AUTO               = 0x200,
	FE_CAN_QPSK                   = 0x400,
	FE_CAN_QAM_16                 = 0x800,
	FE_CAN_QAM_32                 = 0x1000,
	FE_CAN_QAM_64                 = 0x2000,
	FE_CAN_QAM_128                = 0x4000,
	FE_CAN_QAM_256                = 0x8000,
	FE_CAN_QAM_AUTO               = 0x10000,
	FE_CAN_TRANSMISSION_MODE_AUTO = 0x20000,
	FE_CAN_BANDWIDTH_AUTO         = 0x40000,
	FE_CAN_GUARD_INTERVAL_AUTO    = 0x80000,
	FE_CAN_HIERARCHY_AUTO         = 0x100000,
	FE_CAN_8VSB                   = 0x200000,
	FE_CAN_16VSB                  = 0x400000,
	FE_CAN_MUTE_TS                = 0x80000000,
	FE_CAN_CLEAN_SETUP            = 0x40000000
} fe_caps_t;


struct dvb_frontend_info {
	char       name[128];
        fe_type_t  type;
        uint32_t   frequency_min;
        uint32_t   frequency_max;
	uint32_t   frequency_stepsize;
	uint32_t   frequency_tolerance;
	uint32_t   symbol_rate_min;
        uint32_t   symbol_rate_max;
	uint32_t   symbol_rate_tolerance;     /* ppm */
	uint32_t   notifier_delay;            /* ms */
	fe_caps_t  caps;
};


/**
 *  Check out the DiSEqC bus spec available on http://www.eutelsat.org/ for
 *  the meaning of this struct...
 */
struct dvb_diseqc_master_cmd {
        uint8_t msg [6];        /*  { framing, address, command, data [3] } */
        uint8_t msg_len;        /*  valid values are 3...6  */
};


struct dvb_diseqc_slave_reply {
	uint8_t msg [4];        /*  { framing, data [3] } */
	uint8_t msg_len;        /*  valid values are 0...4, 0 means no msg  */
	int     timeout;        /*  return from ioctl after timeout ms with */
};                              /*  errorcode when no message was received  */


typedef enum {
        SEC_VOLTAGE_13,
        SEC_VOLTAGE_18
} fe_sec_voltage_t;


typedef enum {
        SEC_TONE_ON,
        SEC_TONE_OFF
} fe_sec_tone_mode_t;


typedef enum {
        SEC_MINI_A,
        SEC_MINI_B
} fe_sec_mini_cmd_t;


typedef enum {
	FE_HAS_SIGNAL     = 0x01,   /*  found something above the noise level */
	FE_HAS_CARRIER    = 0x02,   /*  found a DVB signal  */
	FE_HAS_VITERBI    = 0x04,   /*  FEC is stable  */
	FE_HAS_SYNC       = 0x08,   /*  found sync bytes  */
	FE_HAS_LOCK       = 0x10,   /*  everything's working... */
	FE_TIMEDOUT       = 0x20,   /*  no lock within the last ~2 seconds */
	FE_REINIT         = 0x40    /*  frontend was reinitialized,  */
} fe_status_t;                      /*  application is recommned to reset */
                                    /*  DiSEqC, tone and parameters */

typedef enum {
        INVERSION_OFF,
        INVERSION_ON,
        INVERSION_AUTO
} fe_spectral_inversion_t;


typedef enum {
        FEC_NONE = 0,
        FEC_1_2,
        FEC_2_3,
        FEC_3_4,
        FEC_4_5,
        FEC_5_6,
        FEC_6_7,
        FEC_7_8,
        FEC_8_9,
        FEC_AUTO
} fe_code_rate_t;


typedef enum {
        QPSK,
        QAM_16,
        QAM_32,
        QAM_64,
        QAM_128,
        QAM_256,
	QAM_AUTO,
	VSB_8,
	VSB_16
} fe_modulation_t;


typedef enum {
	TRANSMISSION_MODE_2K,
	TRANSMISSION_MODE_8K,
	TRANSMISSION_MODE_AUTO
} fe_transmit_mode_t;

typedef enum {
	BANDWIDTH_8_MHZ,
	BANDWIDTH_7_MHZ,
	BANDWIDTH_6_MHZ,
	BANDWIDTH_AUTO
} fe_bandwidth_t;


typedef enum {
	GUARD_INTERVAL_1_32,
	GUARD_INTERVAL_1_16,
	GUARD_INTERVAL_1_8,
	GUARD_INTERVAL_1_4,
	GUARD_INTERVAL_AUTO
} fe_guard_interval_t;


typedef enum {
	HIERARCHY_NONE,
	HIERARCHY_1,
	HIERARCHY_2,
	HIERARCHY_4,
	HIERARCHY_AUTO
} fe_hierarchy_t;


struct dvb_qpsk_parameters {
        uint32_t        symbol_rate;  /* symbol rate in Symbols per second */
        fe_code_rate_t  fec_inner;    /* forward error correction (see above) */
};


struct dvb_qam_parameters {
        uint32_t         symbol_rate; /* symbol rate in Symbols per second */
        fe_code_rate_t   fec_inner;   /* forward error correction (see above) */
        fe_modulation_t  modulation;  /* modulation type (see above) */
};

struct dvb_vsb_parameters {
	fe_modulation_t	modulation;  /* modulation type (see above) */
};

struct dvb_ofdm_parameters {
        fe_bandwidth_t      bandwidth;
        fe_code_rate_t      code_rate_HP;  /* high priority stream code rate */
        fe_code_rate_t      code_rate_LP;  /* low priority stream code rate */
        fe_modulation_t     constellation; /* modulation type (see above) */
        fe_transmit_mode_t  transmission_mode;
        fe_guard_interval_t guard_interval;
        fe_hierarchy_t      hierarchy_information;
};


struct dvb_frontend_parameters {
        uint32_t frequency;       /* (absolute) frequency in Hz for QAM/OFDM */
                                  /* intermediate frequency in kHz for QPSK */
	fe_spectral_inversion_t inversion;
	union {
		struct dvb_qpsk_parameters qpsk;
		struct dvb_qam_parameters  qam;
		struct dvb_ofdm_parameters ofdm;
		struct dvb_vsb_parameters vsb;
	} u;
};


struct dvb_frontend_event {
	fe_status_t status;
	struct dvb_frontend_parameters parameters;
};



#define FE_GET_INFO                _IOR('o', 61, struct dvb_frontend_info)

#define FE_DISEQC_RESET_OVERLOAD   _IO('o', 62)
#define FE_DISEQC_SEND_MASTER_CMD  _IOW('o', 63, struct dvb_diseqc_master_cmd)
#define FE_DISEQC_RECV_SLAVE_REPLY _IOR('o', 64, struct dvb_diseqc_slave_reply)
#define FE_DISEQC_SEND_BURST       _IO('o', 65)  /* fe_sec_mini_cmd_t */

#define FE_SET_TONE                _IO('o', 66)  /* fe_sec_tone_mode_t */
#define FE_SET_VOLTAGE             _IO('o', 67)  /* fe_sec_voltage_t */
#define FE_ENABLE_HIGH_LNB_VOLTAGE _IO('o', 68)  /* int */

#define FE_READ_STATUS             _IOR('o', 69, fe_status_t)
#define FE_READ_BER                _IOR('o', 70, uint32_t)
#define FE_READ_SIGNAL_STRENGTH    _IOR('o', 71, uint16_t)
#define FE_READ_SNR                _IOR('o', 72, uint16_t)
#define FE_READ_UNCORRECTED_BLOCKS _IOR('o', 73, uint32_t)

#define FE_SET_FRONTEND            _IOW('o', 76, struct dvb_frontend_parameters)
#define FE_GET_FRONTEND            _IOR('o', 77, struct dvb_frontend_parameters)
#define FE_GET_EVENT               _IOR('o', 78, struct dvb_frontend_event)


#endif /*_FRONTEND_H_*/

