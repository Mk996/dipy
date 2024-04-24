from typing import Any
from dataclasses import dataclass
import warnings
from abc import ABC, abstractmethod

from dipy.utils.optpkg import optional_package

fury, has_fury, setup_module = optional_package('fury', min_version="0.10.0")

if has_fury:
    from fury import ui
    from fury.data import read_viz_icons


@dataclass
class HorizonUIElement:
    """Dataclass to define properties of horizon ui elements.
    """
    visibility: bool
    selected_value: Any
    obj: Any
    position = (0, 0)
    size = ('auto', 'auto')


class HorizonTab(ABC):
    """Base for different tabs available in horizon.
    """
    def __init__(self):
        self._elements = []
        self.hide = lambda *args: None
        self.show = lambda *args: None

    @abstractmethod
    def build(self, tab_id):
        """Build all the elements under the tab.

        Parameters
        ----------
        tab_id : int
            Id of the tab.
        """

    def _register_elements(self, *args):
        """Register elements for rendering.

        Parameters
        ----------
        *args : HorizonUIElement(s)
            Elements to be register for rendering.
        """
        self._elements += list(args)

    def _toggle_actors(self, checkbox):
        """Toggle actors in the scene. This helps removing the actor to
        interact with actors behind this actor.

        Parameters
        ----------
        checkbox : CheckBox2D
        """
        if '' in checkbox.checked_labels:
            self.show(*self.actors)
        else:
            self.hide(*self.actors)

    def on_tab_selected(self):
        """Implement if require to update something while the tab becomes
        active.
        """
        if hasattr(self, '_actor_toggle'):
            self._toggle_actors(self._actor_toggle.obj)

    @property
    @abstractmethod
    def name(self):
        """Name of the tab.
        """

    @property
    @abstractmethod
    def actors(self):
        """Name of the tab.
        """

    @property
    def tab_id(self):
        """Id of the tab. Reference for Tab Manager to identify the tab.

        Returns
        -------
        int
        """
        return self._tab_id

    @property
    def elements(self):
        """list of underlying FURY ui elements in the tab.
        """
        return self._elements


def build_label(text, font_size=16, bold=False):
    """Simple utility function to build labels.

    Parameters
    ----------
    text : str
    font_size : int, optional
    bold : bool, optional

    Returns
    -------
    label : TextBlock2D
    """

    label = ui.TextBlock2D()
    label.message = text
    label.font_size = font_size
    label.font_family = 'Arial'
    label.justification = 'left'
    label.bold = bold
    label.italic = False
    label.shadow = False
    label.actor.GetTextProperty().SetBackgroundColor(0, 0, 0)
    label.actor.GetTextProperty().SetBackgroundOpacity(0.0)
    label.color = (0.7, 0.7, 0.7)

    return HorizonUIElement(True, text, label)


def build_slider(
        initial_value,
        max_value,
        min_value=0,
        length=450,
        line_width=3,
        radius=8,
        font_size=16,
        text_template='{value:.1f} ({ratio:.0%})',
        on_moving_slider=lambda _slider: None,
        on_value_changed=lambda _slider: None,
        on_change=lambda _slider: None,
        on_handle_released=lambda _istyle, _obj, _slider: None,
        label='',
        label_font_size=16,
        label_style_bold=False,
        is_double_slider=False
):
    """Create a horizon theme based disk-knob slider.

    Parameters
    ----------
    initial_value : float, (float, float)
        Initial value(s) of the slider.
    max_value : float
        Maximum value of the slider.
    min_value : float, optional
        Minimum value of the slider.
    length : int, optional
        Length of the slider.
    line_width : int, optional
        Width of the line on which the disk will slide.
    radius : int, optional
        Radius of the disk handle.
    font_size : int, optional
        Size of the text to display alongside the slider (pt).
    text_template : str, callable, optional
        If str, text template can contain one or multiple of the
        replacement fields: `{value:}`, `{ratio:}`.
        If callable, this instance of `:class:LineSlider2D` will be
        passed as argument to the text template function.
    on_moving_slider : callable, optional
        When the slider is interacted by the user.
    on_value_changed : callable, optional
        When value of the slider changed programmatically.
    on_change : callable, optional
        When value of the slider changed.
    on_handle_released: callable, optional
        When handle released.
    label : str, optional
        Label to ui element for slider
    label_font_size : int, optional
        Size of label text to display with slider
    label_style_bold : bool, optional
        Is label should have bold style.

    Return
    ------
    (label: HorizonUIElement, element(slider): HorizonUIElement)
    """

    if is_double_slider and 'ratio' in text_template:
        warnings.warn('Double slider only support values and not ratio')
        return

    slider_label = build_label(
        label,
        font_size=label_font_size,
        bold=label_style_bold
    )

    if not is_double_slider:
        slider = ui.LineSlider2D(
            initial_value=initial_value,
            max_value=max_value,
            min_value=min_value,
            length=length,
            line_width=line_width,
            outer_radius=radius,
            font_size=font_size,
            text_template=text_template
        )
    else:
        slider = ui.LineDoubleSlider2D(
            initial_values=initial_value,
            max_value=max_value,
            min_value=min_value,
            length=length,
            line_width=line_width,
            outer_radius=radius,
            font_size=font_size,
            text_template=text_template
        )

    slider.on_moving_slider = on_moving_slider
    slider.on_value_changed = on_value_changed
    slider.on_change = on_change

    if not is_double_slider:
        slider.handle_events(slider.handle.actor)
        slider.on_left_mouse_button_released = on_handle_released

    slider.default_color = (1., .5, .0)
    slider.track.color = (.8, .3, .0)
    slider.active_color = (.9, .4, .0)
    if not is_double_slider:
        slider.handle.color = (1., .5, .0)
    else:
        slider.handles[0].color = (1., .5, .0)
        slider.handles[1].color = (1., .5, .0)

    return (
        slider_label,
        HorizonUIElement(True, initial_value, slider)
    )


def build_checkbox(
        labels=None,
        checked_labels=None,
        padding=1,
        font_size=16,
        on_change=lambda _checkbox: None
):
    """Create horizon theme checkboxes.

    Parameters
    ----------
    labels : list(str), optional
        List of labels of each option.
    checked_labels: list(str), optional
        List of labels that are checked on setting up.
    padding : float, optional
        The distance between two adjacent options element
    font_size : int, optional
        Size of the text font.
    on_change : callback, optional
        When checkbox value changed

    Returns
    -------
    checkbox : HorizonUIElement
    """

    if labels is None or not labels:
        warnings.warn('At least one label needs to be to create checkboxes')
        return

    if checked_labels is None:
        checked_labels = ()

    checkboxes = ui.Checkbox(
        labels=labels,
        checked_labels=checked_labels,
        padding=padding,
        font_size=font_size
    )

    checkboxes.on_change = on_change

    return HorizonUIElement(True, checked_labels, checkboxes)


def build_radio_button(
        labels=None,
        checked_labels=None,
        padding=1,
        font_size=16,
        on_change=lambda _checkbox: None
):
    """Create horizon theme radio buttons.

    Parameters
    ----------
    labels : list(str), optional
        List of labels of each option.
    checked_labels: list(str), optional
        List of labels that are checked on setting up.
    padding : float, optional
        The distance between two adjacent options element
    font_size : int, optional
        Size of the text font.
    on_change : callback, optional
        When radio button value changed

    Returns
    -------
    radio : HorizonUIElement
    """

    if labels is None or not labels:
        warnings.warn('At least one label needs to be to create radio buttons')
        return

    if checked_labels is None:
        checked_labels = ()

    radio = ui.RadioButton(
        labels=labels,
        checked_labels=checked_labels,
        padding=padding,
        font_size=font_size
    )

    radio.on_change = on_change

    return HorizonUIElement(True, checked_labels, radio)


def build_switcher(
        items=None,
        label='',
        initial_selection=0,
        on_prev_clicked=lambda _selected_value: None,
        on_next_clicked=lambda _selected_value: None,
        on_value_changed=lambda _selected_idx, _selected_value: None,
):
    """Create horizon theme switcher.

    Parameters
    ----------
    items : list, optional
        dictionaries with keys 'label' and 'value'. Label will be used to show
        it to user and value will be used for selection.
    label : str, optional
        label for the switcher.
    initial_selection : int, optional
        index of the selected item initially.
    on_prev_clicked : callback, optional
        method providing a callback when prev value is selected in switcher.
    on_next_clicked : callback, optional
        method providing a callback when next value is selected in switcher.
    on_value_changed : callback, optional
        method providing a callback when either prev or next value selected in
        switcher.

    Returns
    -------
    HorizonCombineElement(
        label: HorizonUIElement,
        element(switcher): HorizonUIElement)

    Notes
    -----
    switcher: consists 'obj' which is an array providing FURY UI elements used.
    """
    if items is None:
        warnings.warn('No items passed in switcher')
        return

    num_items = len(items)

    if initial_selection >= num_items:
        initial_selection = 0

    switch_label = build_label(text=label)
    selection_label = build_label(
        text=items[initial_selection]['label']).obj

    left_button = ui.Button2D(
            icon_fnames=[('left', read_viz_icons(fname='circle-left.png'))],
            size=(25, 25))
    right_button = ui.Button2D(
            icon_fnames=[('right', read_viz_icons(fname='circle-right.png'))],
            size=(25, 25))

    switcher = HorizonUIElement(True, [initial_selection,
                                items[initial_selection]['value']],
                                [left_button, selection_label, right_button])

    def left_clicked(_i_ren, _obj, _button):
        selected_id = switcher.selected_value[0] - 1
        if selected_id < 0:
            selected_id = num_items - 1
        value_changed(selected_id)
        on_prev_clicked(items[selected_id]['value'])
        on_value_changed(selected_id, items[selected_id]['value'])

    def right_clicked(_i_ren, _obj, _button):
        selected_id = switcher.selected_value[0] + 1
        if selected_id >= num_items:
            selected_id = 0
        value_changed(selected_id)
        on_next_clicked(items[selected_id]['value'])
        on_value_changed(selected_id, items[selected_id]['value'])

    def value_changed(selected_id):
        switcher.selected_value[0] = selected_id
        switcher.selected_value[1] = items[selected_id]['value']
        selection_label.message = items[selected_id]['label']

    left_button.on_left_mouse_button_clicked = left_clicked
    right_button.on_left_mouse_button_clicked = right_clicked

    return (
        switch_label,
        switcher
    )


def build_tab_ui(
        position,
        size,
        tab_count,
        active_color=(1, 1, 1),
        inactive_color=(0.5, 0.5, 0.5),
        draggable=True,
        active_tab=None
):

    if (active_tab is None):
        active_tab = tab_count - 1

    tab_ui = ui.TabUI(position=position, size=size, active_color=active_color,
                      inactive_color=inactive_color, draggable=draggable,
                      startup_tab_id=active_tab)

    return HorizonUIElement(True, None, tab_ui)
