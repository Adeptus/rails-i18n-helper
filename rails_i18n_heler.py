import sublime, sublime_plugin
import os, re, textwrap
import yaml

def is_rails_view(path):
  return True if ( re.search(r"(?:\\|\/)app(?:\\|\/)views$", path) ) else False

class RailsI18nHelperCommand(sublime_plugin.TextCommand):
  edit         = None

  def run(self, edit):
    self.edit         = edit
    self.get_selected_text()

  # Get the selected text
  def get_selected_text(self):
    for region in self.view.sel():
      if not region.empty():
        selected_text = self.view.substr(region)
        self.create_text_and_key(selected_text)
      else:
        self.display_message("First you have to select text!")

  # Create the file
  def create_text_and_key(self, selected_text):
    # The source file's pathreload
    source = self.view.file_name()
    
    key_link = selected_text.replace(" ", "_")[0:30].strip("_").lower()

    # Get the file path
    source_path      = os.path.dirname(source)
    fileName         = os.path.basename(source).replace(".html", "").replace(".erb", "").replace(".haml", "").strip("_")
    rails_view_path  = os.path.dirname(source_path)
    rails_view_path2 = os.path.dirname(rails_view_path)
    
    if is_rails_view(source_path):
      # If we're a rails view file, change the target path to the rails root and add path to locales
      target_file = os.path.abspath(source_path + "/../../") + "/config/locales/en.yml"
      yaml_dict = yaml.load(file(target_file, 'r'))
      if not yaml_dict["en"].has_key(str(fileName)):
        yaml_dict["en"][str(fileName)] = {}
      yaml_dict["en"][str(fileName)][str(key_link)] = str(selected_text)
      rails_view_path = source_path

    if is_rails_view(rails_view_path):
      # If we're a rails view file, change the target path to the rails root and add path to locales
      target_file = os.path.abspath(source_path + "/../../../") + "/config/locales/en.yml"
      key = source_path.replace(rails_view_path, "").strip("/")
      yaml_dict = yaml.load(file(target_file, 'r'))
      if not yaml_dict["en"].has_key(str(key)):
        yaml_dict["en"][str(key)] = {}
      if not yaml_dict["en"][str(key)].has_key(str(fileName)):
        yaml_dict["en"][str(key)][str(fileName)] = {}
      yaml_dict["en"][str(key)][str(fileName)][str(key_link)] = str(selected_text)
      rails_view_path = rails_view_path

    if is_rails_view(rails_view_path2):
      # If we're a rails view file, change the target path to the rails root and add path to locales
      target_file = os.path.abspath(source_path + "/../../../../") + "/config/locales/en.yml"
      key = rails_view_path.replace(rails_view_path2, "").strip("/")
      key2 = source_path.replace(rails_view_path, "").strip("/")
      yaml_dict = yaml.load(file(target_file, 'r'))
      if not yaml_dict["en"].has_key(str(key)):
        yaml_dict["en"][str(key)] = {}
      if not yaml_dict["en"][str(key)].has_key(str(key2)):
        yaml_dict["en"][str(key)][str(key2)] = {}
      if not yaml_dict["en"][str(key)][str(key2)].has_key(str(fileName)):
        yaml_dict["en"][str(key)][str(key2)][str(fileName)] = {}
      yaml_dict["en"][str(key)][str(key2)][str(fileName)][str(key_link)] = str(selected_text)
      rails_view_path = rails_view_path2


    if os.path.isfile(target_file):
      #insert key to view file
      stream = file(target_file, 'w')
      yaml.dump(yaml_dict, stream, default_flow_style=False) 
      stream.close()
      self.insert_key_link(key_link, source)
    else:
      self.display_message(target_file + " not exist")


  # Insert the key code
  def insert_key_link(self, key_link, source):
    # Handle different file types
    if source.endswith(".haml"):
      code_replace = '= t("{0}")'
    elif source.endswith( (".erb") ):  
      code_replace = '<%= t("{0}") %>'
    else:
      self.display_message("You're using an unsupported file type! The string was created in yml but not, linked automatically.")

    # Replace the selected text with the appropriate key code
    for region in self.view.sel():
      if region.empty():
        point = region.begin()
        self.view.insert(self.edit, point, code_replace.format("." + key_link) )
      else:
        self.view.replace(self.edit, region, code_replace.format("." + key_link) )

    self.display_message(key_link + ' Created Successfully!')


  def display_message(self, value):
      sublime.active_window().active_view().set_status("create_i18_from_text", value)