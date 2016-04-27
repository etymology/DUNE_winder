#! /usr/bin/env python

import os
import os.path
import shlex
import shutil
import subprocess
import sys

class EnvironmentPaths:
   RootPath = r"C:/bin/"

   WinderSourcePath = RootPath + r"source"
   ScriptSourcePath = RootPath + r"scripts"

class SetupManager( object ):
   def __init__( self, resources_directory = None, **kwargs ):
      self.resources_directory = resources_directory

      self._initialize()

   def _initialize( self ):
      self.python_exe_path = sys.executable

      python_directory_path = os.path.dirname( self.python_exe_path )
      self.python_pip_path = os.path.join( python_directory_path, "Scripts", "pip.exe" )

   def setup( self, source_code_path, **kwargs ):
      if source_code_path is not None:
         if not os.path.isabs( source_code_path ):
            source_code_path = os.path.abspath( source_code_path )
         source_code_path = os.path.normcase( source_code_path )

         target_path = os.path.join( os.path.normpath( EnvironmentPaths.WinderSourcePath ), os.path.split( source_code_path )[ 1 ] )

         self._install_libraries( **kwargs )
         self._install_scripts( target_path, os.path.normpath( EnvironmentPaths.ScriptSourcePath ), **kwargs )
         self._install_source_code( source_code_path, target_path )
      else:
         raise ValueError( "Source code path cannot be None." )

   def _update_pip( self, **kwargs ):
      action = "install --upgrade"
      packages = "pip wheel setuptools"

      self._invoke_pip( action, packages )

   def _invoke_pip( self, action, *args, **kwargs ):
      arguments = [ action ]
      if len( args ) > 0:
         arguments.extend( args )

      process_args = [ self.python_pip_path ]
      for item in arguments:
         process_args.extend( shlex.split( item ) )

      subprocess.call( process_args )

   def _install_libraries( self, **kwargs ):
      self._update_pip( **kwargs )

      self._install_kivy( **kwargs )
      self._install_pycomm( **kwargs )

   def _install_kivy( self, **kwargs ):
      self._invoke_pip( "install", "docutils pygments pypiwin32 kivy.deps.sdl2 kivy.deps.glew kivy.deps.gstreamer", "--extra-index-url https://kivy.org/downloads/packages/simple/", **kwargs )
      self._invoke_pip( "install", "kivy", **kwargs )

   def _install_pycomm( self, **kwargs ):
      self._invoke_pip( "install", "pycomm", **kwargs )

   def _install_scripts( self, target_source_code_directory, target_directory = None, **kwargs ):
      self._create_directory( target_directory, **kwargs )
      self._write_run_simulated_server_script( target_source_code_directory, "run_simulated_server.bat", target_directory, **kwargs )
      self._write_run_console_client_script( "run_console_client.bat", target_directory, **kwargs )

   def _create_directory( self, target_directory, **kwargs ):
      if target_directory is not None:
         if not os.path.exists( target_directory ):
            os.makedirs( target_directory )
         elif not os.path.isdir( target_directory ):
            raise IOError( "Target directory '{}' already exists and is not a directory.".format( *target_directory ) )
      else:
         raise ValueError( "Cannot create directory: directory cannot be None." )

   def _write_file( self, file_contents, name, directory = None, **kwargs ):
      if directory is None:
         directory = os.getcwd()

      if os.path.isabs( name ):
         file_name = name
      else:
         file_name = os.path.join( directory, name )

      with open( file_name, "w" ) as f:
         f.write( file_contents )

      return file_name

   def _write_run_simulated_server_script( self, target_source_directory, name, directory = None, **kwargs ):
      file_contents = \
"""@echo off

cd "{}"
call "{}" main.py simulated debug=False

exit /b
""".format( os.path.join( target_source_directory, "Control" ), self.python_exe_path )

      return self._write_file( file_contents, name, directory, **kwargs )

   def _write_run_console_client_script( self, name, directory = None, **kwargs ):
      file_contents = \
"""@echo off

cd "{}"
call "{}" -m winder.client.console

exit /b
""".format( os.path.normpath( EnvironmentPaths.WinderSourcePath ), self.python_exe_path )

      return self._write_file( file_contents, name, directory )

   def _install_source_code( self, source_path, target_path, overwrite = True ):
      if not os.path.exists( source_path ):
         raise ValueError( "Source code path '{}' does not exist.".format( source_path ) )
      elif not os.path.isdir( source_path ):
         raise ValueError( "Source code path '{}' must be a directory.".format( source_path ) )
      else:
         if target_path is not None:
            if not os.path.isabs( target_path ):
               target_path = os.path.abspath( target_path )

            if os.path.exists( target_path ):
               if os.path.isdir( target_path ):
                  if overwrite:
                     shutil.rmtree( target_path )
                  else:
                     raise ValueError( "Cannot install source code from '{}' at '{}': previous source code already exists.".format( source_path, target_path ) )
               else:
                  raise ValueError( "Cannot install source code from '{}' at '{}': a non-directory file already exists at the location.".format( source_path, target_path ) )

            shutil.copytree( source_path, target_path )
         else:
            raise ValueError( "Target installation directory cannot be None." )

def main( args = None ):
   if args is None:
      args = sys.argv[ 1 : ]

   script_path = sys.argv[ 0 ]
   script_dir = os.path.dirname( script_path )

   setup_manager = SetupManager( os.path.join( script_dir, "resources" ) )
   setup_manager.setup( args[ 0 ] )

if __name__ == "__main__":
   main()
