from dipy.viz.horizon.tab.base import (HorizonTab, build_label, build_tab_ui,
                                       build_slider, build_checkbox,
                                       build_switcher, build_radio_button)
from dipy.viz.horizon.tab.cluster import ClustersTab
from dipy.viz.horizon.tab.peak import PeaksTab
from dipy.viz.horizon.tab.roi import ROIsTab
from dipy.viz.horizon.tab.slice import SlicesTab
from dipy.viz.horizon.tab.surface import SurfaceTab
from dipy.viz.horizon.tab.manager import TabManager

__all__ = [
    'HorizonTab', 'TabManager', 'ClustersTab', 'PeaksTab', 'ROIsTab',
    'SlicesTab', 'build_label', 'build_slider', 'build_checkbox',
    'build_switcher', 'SurfaceTab', 'build_radio_button', 'build_tab_ui']
