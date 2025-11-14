#!/usr/bin/env -S PYTHONPATH=../../../tools/extract-utils python3
#
# SPDX-FileCopyrightText: 2024 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0
#

from extract_utils.fixups_blob import (
    blob_fixup,
    blob_fixups_user_type,
)
from extract_utils.fixups_lib import (
    lib_fixups,
    lib_fixups_user_type,
)
from extract_utils.main import (
    ExtractUtils,
    ExtractUtilsModule,
)

namespace_imports = [
    'device/xiaomi/veux',
    'hardware/qcom-caf/sm8350',
    'hardware/qcom-caf/wlan',
    'hardware/xiaomi',
    'vendor/qcom/opensource/commonsys-intf/display',
    'vendor/qcom/opensource/commonsys/display',
    'vendor/qcom/opensource/dataservices',
    'vendor/qcom/opensource/display',
]

def lib_fixup_vendor_suffix(lib: str, partition: str, *args, **kwargs):
    return f'{lib}_{partition}' if partition == 'vendor' else None

lib_fixups: lib_fixups_user_type = {
    **lib_fixups,
    (
        'com.qualcomm.qti.dpm.api@1.0',
        'libmmosal',
        'vendor.qti.diaghal@1.0',
        'vendor.qti.hardware.fm@1.0',
        'vendor.qti.hardware.wifidisplaysession@1.0',
        'vendor.qti.ims.callcapability@1.0',
        'vendor.qti.imsrtpservice@3.0',
    ): lib_fixup_vendor_suffix,
}

blob_fixups: blob_fixups_user_type = {
    'odm/etc/build_*.prop': blob_fixup()
        .regex_replace(r'.*marketname.*\n', r'')
        .regex_replace(r'cert', r'model'),
    
    'system_ext/etc/init/wfdservice.rc': blob_fixup()
        .regex_replace(r'^(?!service)(.*)wfdservice$', r'\g<1>wfdservice64'),
    
    'system_ext/lib64/libwfdnative.so': blob_fixup()
        .replace_needed('android.hidl.base@1.0.so', 'libinput_shim.so'),
    
    'vendor/etc/camera/camxoverridesettings.txt': blob_fixup()
        .regex_replace(r'0x10080', r'0')
        .regex_replace(r'0x1F', r'0x0'),
    
    'vendor/etc/init/init.batterysecret.rc': blob_fixup()
        .regex_replace(r'on charger', r'on property:init.svc.vendor.charger=running'),
    
    'vendor/lib64/android.hardware.secure_element@1.0-impl.so': blob_fixup()
        .remove_needed('android.hidl.base@1.0.so'),

    ('vendor/lib64/libalLDC.so', 'vendor/lib64/libalhLDC.so'): blob_fixup()
        .clear_symbol_version('AHardwareBuffer_allocate')
        .clear_symbol_version('AHardwareBuffer_describe')
        .clear_symbol_version('AHardwareBuffer_lock')
        .clear_symbol_version('AHardwareBuffer_release')
        .clear_symbol_version('AHardwareBuffer_unlock'),

    'vendor/lib64/libgoodixhwfingerprint.so': blob_fixup()
        .replace_needed('libvendor.goodix.hardware.biometrics.fingerprint@2.1.so', 'vendor.goodix.hardware.biometrics.fingerprint@2.1.so'),

    ('vendor/lib64/libdlbdsservice.so', 
     'vendor/lib/libstagefright_soft_ac4dec.so', 
     'vendor/lib/libstagefright_soft_ddpdec.so'): blob_fixup()
        .replace_needed('libstagefright_foundation.so', 'libstagefright_foundation-v33.so'),

    'vendor/etc/libnfc-sn100.conf': blob_fixup()
        .regex_replace(r'(DEFAULT_ISODEP_ROUTE.*?)0x01', r'\g<1>0xC0')
        .regex_replace(r'(DEFAULT_SYS_CODE_ROUTE.*?)0x00', r'\g<1>0xC0')
        .regex_replace(r'(DEFAULT_OFFHOST_ROUTE.*?)0x01', r'\g<1>0xC0')
        .regex_replace(r'(OFFHOST_ROUTE_ESE.*?)01', r'\g<1>C0')
        .regex_replace(r'$', r'\nDEFAULT_NFCF_ROUTE=0xC0'),

    ('vendor/lib64/libwvhidl.so','vendor/lib64/mediadrm/libwvdrmengine.so'): blob_fixup()
        .add_needed('libcrypto_shim.so'),

    ('system_ext/lib/libwfdmmsrc_system.so','system_ext/lib64/libwfdmmsrc_system.so'): blob_fixup()
        .add_needed('libgui_shim.so'),
    
    ('system_ext/lib/libwfdservice.so','system_ext/lib64/libwfdservice.so'): blob_fixup()
        .replace_needed('android.media.audio.common.types-V2-cpp.so', 'android.media.audio.common.types-V4-cpp.so'),
}


module = ExtractUtilsModule(
    'veux',
    'xiaomi',
    blob_fixups=blob_fixups,
    lib_fixups=lib_fixups,
    namespace_imports=namespace_imports,
)

if __name__ == '__main__':
    utils = ExtractUtils.device(module)
    utils.run()