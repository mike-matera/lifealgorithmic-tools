"""
Helpers for LVM and partitioned disks.
"""

import subprocess


def capture(cmd, **kwargs):
    proc = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, universal_newlines=True,
                          **kwargs)
    return proc.stdout


class PartitionedDisk:

    def __init__(self, disk):
        txt = capture('parted -m -s {} print'.format(disk), check=False)
        lines = txt.split('\n')[1:-1]
        self.device, self.device_size, self.device_type, _, _, self.label_type, self.id, _ = lines[0].split(':')
        self.device_size = self.normalize(self.device_size)

        self.partitions = []
        for line in lines[1:]:
            pieces = line.split(':')

            start = self._normalize(pieces[1])
            end = self._normalize(pieces[2])
            size = self._normalize(pieces[3])

            part = {
                'start': start,
                'end': end,
                'size': size,
                'fs': pieces[4],
                'label': pieces[5],
            }
            self.partitions.append(part)

    def _normalize(self, number):
        m = re.match(r'(\d+)(k|M|G)B', number)
        assert m is not None, \
            """Internal error could not connvert a number from parted!"""

        if m.group(2) == 'k':
            mult = 1000
        elif m.group(2) == 'M':
            mult = 1000000
        elif m.group(2) == 'G':
            mult = 1000000000

        return int(m.group(1)) * mult


class LVMData:
    def load(self, cmd, fields, name):
        ccmd = cmd + ' -o ' + ','.join(fields) + ' --noheadings --separator : --units b ' + name
        txt = capture(ccmd, check=True)
        data = txt.split(':')
        for idx, field in enumerate(fields):
            setattr(self, field, data[idx].strip())


class VolumeGroup(LVMData):
    fields = ['vg_fmt', 'vg_uuid', 'vg_name', 'vg_attr', 'vg_permissions', 'vg_extendable', 'vg_exported', 'vg_partial',
              'vg_allocation_policy', 'vg_clustered', 'vg_size', 'vg_free', 'vg_sysid', 'vg_systemid', 'vg_locktype',
              'vg_lockargs', 'vg_extent_size', 'vg_extent_count', 'vg_free_count', 'max_lv', 'max_pv', 'pv_count',
              'vg_missing_pv_count', 'lv_count', 'snap_count', 'vg_seqno', 'vg_tags', 'vg_profile', 'vg_mda_count',
              'vg_mda_used_count', 'vg_mda_free', 'vg_mda_size', 'vg_mda_copies']

    def __init__(self, name):
        try:
            self.load('vgs', VolumeGroup.fields, name)
        except:
            assert False, \
                '''There doesn't appear to be a volume group named ''' + name


class LogicalVolume(LVMData):
    fields = ['lv_uuid', 'lv_name', 'lv_full_name', 'lv_path', 'lv_dm_path', 'lv_parent', 'lv_layout', 'lv_role',
              'lv_initial_image_sync', 'lv_merging', 'lv_converting', 'lv_allocation_policy', 'lv_fixed_minor',
              'lv_merge_failed', 'lv_snapshot_invalid', 'lv_when_full', 'lv_active', 'lv_active_locally',
              'lv_active_remotely', 'lv_major', 'lv_minor', 'lv_read_ahead', 'lv_size', 'lv_metadata_size', 'seg_count',
              'origin', 'origin_uuid', 'origin_size', 'lv_ancestors', 'lv_descendants', 'data_percent', 'snap_percent',
              'metadata_percent', 'copy_percent', 'sync_percent', 'raid_mismatch_count', 'raid_write_behind',
              'raid_min_recovery_rate', 'move_pv', 'move_pv_uuid', 'convert_lv', 'convert_lv_uuid', 'mirror_log',
              'mirror_log_uuid', 'data_lv', 'data_lv_uuid', 'metadata_lv', 'metadata_lv_uuid', 'pool_lv',
              'pool_lv_uuid', 'lv_tags', 'lv_profile', 'lv_lockargs', 'lv_time', 'lv_host', 'lv_modules']

    def __init__(self, name):
        try:
            self.load('lvs', LogicalVolume.fields, name)
        except:
            assert False, \
                '''There doesn't appear to be a logical volume named ''' + name


class PhysicalVolume(LVMData):
    fields = ['pv_fmt', 'pv_uuid', 'dev_size', 'pv_name', 'pv_mda_free', 'pv_mda_size', 'pe_start', 'pv_size',
              'pv_free', 'pv_used', 'pv_attr', 'pv_allocatable', 'pv_exported', 'pv_missing', 'pv_pe_count',
              'pv_pe_alloc_count', 'pv_tags', 'pv_mda_count', 'pv_mda_used_count', 'pv_ba_start', 'pv_ba_size',
              'vg_name']

    def __init__(self, name):
        try:
            self.load('pvs', PhysicalVolume.fields, name)
        except Exception as e:
            assert False, \
                '''No physical volume on device ''' + name

