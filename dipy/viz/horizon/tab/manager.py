import warnings

import numpy as np

from dipy.viz.horizon.util import show_ellipsis
from dipy.viz.horizon.tab import build_tab_ui


class TabManager:
    """
    A Manager for tabs of the table panel.

    Attributes
    ----------

    tab_ui : TabUI
        Underlying FURY TabUI object.
    """
    def __init__(
        self,
        tabs,
        win_size,
        on_tab_changed,
        add_to_scene,
        remove_from_scene,
        sync_slices=False,
        sync_volumes=False,
        sync_peaks=False
    ):

        self._tabs = tabs
        self._add_to_scene = add_to_scene
        self._remove_from_scene = remove_from_scene
        self._synchronize_slices = sync_slices
        self._synchronize_volumes = sync_volumes
        self._synchronize_peaks = sync_peaks

        win_width, _win_height = win_size

        self._tab_size = (1280, 240)
        self._x_pad = np.rint((win_width - self._tab_size[0]) / 2)

        self._active_tab_id = len(self._tabs) - 1

        self.tab_changed = on_tab_changed

        slices_tabs = list(
            filter(
                lambda x: x.__class__.__name__ == 'SlicesTab', self._tabs
            )
        )
        if not self._synchronize_slices and slices_tabs:
            msg = 'Images are of different dimensions, ' \
                + 'synchronization of slices will not work'
            warnings.warn(msg)

        for tab_id, tab in enumerate(tabs):
            tab.hide = self._hide_elements
            tab.show = self._show_elements
            tab.build(tab_id)
            if tab.__class__.__name__ == 'SlicesTab':
                tab.on_volume_change = self.synchronize_volumes
            if tab.__class__.__name__ in ['SlicesTab', 'PeaksTab']:
                tab.on_slice_change = self.synchronize_slices

        self._tab_ui = None
        self._render_tabs()
        self._tab_ui.obj.on_change = self._tab_selected

    def handle_text_overflows(self):
        for tab_id, tab in enumerate(self._tabs):
            self._handle_title_overflow(
                tab.name,
                self._tab_ui.obj.tabs[tab_id].text_block
            )
            for element in tab.elements:
                if (not element.size[0] == 'auto' and
                        element.obj.__class__.__name__ == 'TextBlock2D' and
                        isinstance(element.position, tuple)):
                    element.obj.message = show_ellipsis(
                        element.selected_value,
                        element.obj.size[0],
                        element.size[0])

    def _handle_title_overflow(self, title_text, title_block):
        """Handle overflow of the tab title and show ellipsis if required.

        Parameters
        ----------
        title_text : str
            Text to be shown on the tab.
        title_block : TextBlock2D
            Fury UI element for holding the title of the tab.
        """
        tab_text = title_text.split('.', 1)[0]
        title_block.message = tab_text
        available_space, _ = self._tab_size
        text_size = title_block.size[0]
        max_width = (available_space / len(self._tabs)) - 15
        title_block.message = show_ellipsis(tab_text, text_size, max_width)

    def _render_tab_elements(self, tab_id, elements):
        for element in elements:
            if isinstance(element.position, list):
                for i, position in enumerate(element.position):
                    self._tab_ui.obj.add_element(
                        tab_id, element.obj[i], position)
            else:
                self._tab_ui.obj.add_element(
                    tab_id, element.obj, element.position)

    def _hide_elements(self, *args):
        """Hide elements from the scene.

        Parameters
        ----------
        *args : HorizonUIElement or FURY actors
            Elements to be hidden.
        """
        self._remove_from_scene(*self._get_vtkActors(*args))

    def _show_elements(self, *args):
        """Show elements in the scene.

        Parameters
        ----------
        *args : HorizonUIElement or FURY actors
            Elements to be hidden.
        """
        self._add_to_scene(*self._get_vtkActors(*args))

    def _get_vtkActors(self, *args):
        elements = []
        vtk_actors = []
        for element in args:
            if (element.__class__.__name__ == 'HorizonUIElement'):
                if isinstance(element.obj, list):
                    for obj in element.obj:
                        elements.append(obj)
                else:
                    elements.append(element.obj)
            else:
                elements.append(element)

        for element in elements:
            if (hasattr(element, '_get_actors') and
                    callable(element._get_actors)):
                vtk_actors += element.actors
            else:
                vtk_actors.append(element)
        return vtk_actors

    def _tab_selected(self, tab_ui):
        if self._active_tab_id == tab_ui.active_tab_idx:
            self._active_tab_id = -1
            return

        self._active_tab_id = tab_ui.active_tab_idx

        current_tab = self._tabs[self._active_tab_id]
        self.tab_changed(current_tab.actors)
        current_tab.on_tab_selected()

    def add_tab(self, tab):

        tab_id = len(self._tabs)
        self._tabs.append(tab)

        tab.hide = self._hide_elements
        tab.show = self._show_elements
        tab.build(tab_id)

        if tab.__class__.__name__ == 'SlicesTab':
            tab.on_volume_change = self.synchronize_volumes
        if tab.__class__.__name__ in ['SlicesTab', 'PeaksTab']:
            tab.on_slice_change = self.synchronize_slices
        self._render_tabs()

    def _render_tabs(self):
        self._tab_ui = build_tab_ui(
            (self._x_pad, 5),
            self._tab_size,
            len(self._tabs),
            active_tab=self._active_tab_id
        )

        for tab in self._tabs:
            self._render_tab_elements(tab.tab_id, tab.elements)

    def reposition(self, win_size):
        """
        Reposition the tabs panel.

        Parameters
        ----------
        win_size : (float, float)
            size of the horizon window.
        """
        win_width, _win_height = win_size
        x_pad = np.rint((win_width - self._tab_size[0]) / 2)
        self._tab_ui.obj.position = (x_pad, 5)

    def synchronize_slices(self, active_tab_id, x_value, y_value, z_value):
        """
        Synchronize slicers for all the images and peaks.

        Parameters
        ----------
        active_tab_id: int
            tab_id of the action performing tab
        x_value: float
            x-value of the active slicer
        y_value: float
            y-value of the active slicer
        z_value: float
            z-value of the active slicer
        """

        if not self._synchronize_slices and not self._synchronize_peaks:
            return

        for tab in self._get_non_active_tabs(active_tab_id,
                                             ['SlicesTab', 'PeaksTab']):
            tab.update_slices(x_value, y_value, z_value)

    def synchronize_volumes(self, active_tab_id, value):
        """Synchronize volumes for all the images with volumes.

        Parameters
        ----------
        active_tab_id : int
            tab_id of the action performing tab
        value : float
            volume value of the active volume slider

        """

        if not self._synchronize_volumes:
            return

        for slices_tab in self._get_non_active_tabs(active_tab_id):
            slices_tab.update_volume(value)

    def _get_non_active_tabs(self, active_tab_id, types=['SlicesTab']):
        """Get tabs which are not active and slice tabs.

        Parameters
        ----------
        active_tab_id : int
        types : list(str), optional

        Returns
        -------
        list
        """
        return list(
            filter(
                lambda x: x.__class__.__name__ in types
                and not x.tab_id == active_tab_id, self._tabs
            )
        )

    @property
    def tab_ui(self):
        """HorizonUIElement with TabUI object.
        """
        return self._tab_ui
