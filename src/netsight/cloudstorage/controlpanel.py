from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.z3cform import layout
from z3c.form import form

from .interfaces import ICloudStorageSettings

class CloudStorageControlPanelForm(RegistryEditForm):
    form.extends(RegistryEditForm)
    schema = ICloudStorageSettings


CloudStorageControlPanelView = layout.wrap_form(
    CloudStorageControlPanelForm,
    ControlPanelFormWrapper
)
CloudStorageControlPanelView.label = u"CloudStorage settings"