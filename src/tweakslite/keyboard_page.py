from .utils import format_keyboard_option

class KeyboardPage:
    def create_option_row(self, option_text):
        """Creates a row for a keyboard option"""
        label = Gtk.Label()
        # Format the text before setting it as markup
        safe_text = format_keyboard_option(option_text)
        label.set_markup(safe_text)
        return label

    def load_keyboard_options(self, options):
        """Loads keyboard options into the UI"""
        for option in options:
            # Format the option text before creating the row
            row = self.create_option_row(option)
            self.options_list.append(row)