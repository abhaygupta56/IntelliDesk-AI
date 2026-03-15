# src/automation/file_ops.py

"""
File Operations Module - SAFE VERSION
Features:
- Create/Delete files and folders
- Rename/Move/Copy files
- Search files
- Organize folders
- Safety mechanisms
"""

import os
import shutil
import time
from pathlib import Path
from datetime import datetime
import subprocess
from typing import Dict, Any
from src.utils.logger import Logger
from src.database.db_manager import DatabaseManager

logger = Logger.get_logger("FileOps")


class SafetyManager:
    """Safety checks for file operations"""
    
    PROTECTED_PATHS = [
        r"C:\Windows",
        r"C:\Program Files",
        r"C:\Program Files (x86)",
        r"C:\System Volume Information",
        r"C:\ProgramData",
        r"C:\Users\Public",
        r"C:\Boot",
        r"C:\Recovery",
    ]
    
    CRITICAL_EXTENSIONS = [
        '.sys', '.dll', '.exe', '.msi', '.bat', '.cmd', '.ps1',
        '.vbs', '.reg', '.ini', '.inf', '.dat'
    ]
    
    MAX_FILE_SIZE = 500 * 1024 * 1024  # 500 MB
    MAX_FOLDER_SIZE = 5 * 1024 * 1024 * 1024  # 5 GB
    
    @staticmethod
    def is_protected_path(path: str) -> bool:
        """Check if path is in protected areas"""
        try:
            path_obj = Path(path).resolve()
            path_str = str(path_obj).lower()
            
            for protected in SafetyManager.PROTECTED_PATHS:
                if path_str.startswith(protected.lower()):
                    return True
            
            # Root drive protection
            if len(path_obj.parts) <= 2 and path_obj.drive.upper() == "C:":
                return True
            
            return False
        except:
            return True  # If error, assume protected
    
    @staticmethod
    def is_critical_file(path: str) -> bool:
        """Check if file has critical extension"""
        extension = Path(path).suffix.lower()
        return extension in SafetyManager.CRITICAL_EXTENSIONS
    
    @staticmethod
    def get_size(path: str) -> int:
        """Get file or folder size"""
        path_obj = Path(path)
        
        if path_obj.is_file():
            return path_obj.stat().st_size
        
        total = 0
        try:
            for item in path_obj.rglob("*"):
                if item.is_file():
                    total += item.stat().st_size
        except:
            pass
        return total
    
    @staticmethod
    def validate_operation(path: str, operation: str) -> Dict[str, Any]:
        """Validate if operation is safe"""
        
        # Check protected path
        if SafetyManager.is_protected_path(path):
            return {
                "safe": False,
                "reason": "protected_path",
                "message": f"⛔ Cannot {operation} protected system path"
            }
        
        # Check critical file
        if operation in ["delete", "move", "rename"] and SafetyManager.is_critical_file(path):
            return {
                "safe": False,
                "reason": "critical_file",
                "message": f"⚠️ Critical system file - operation blocked"
            }
        
        # Check path exists (for delete/move/rename/copy)
        if operation in ["delete", "move", "rename", "copy"]:
            if not Path(path).exists():
                return {
                    "safe": False,
                    "reason": "not_found",
                    "message": f"❌ Path not found: {path}"
                }
        
        return {"safe": True, "message": "✅ Safe"}


class FileManager:
    """Core file operations with safety"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.safety = SafetyManager()
        self._init_file_history()
    
    def _init_file_history(self):
        """Track file operations"""
        try:
            conn = self.db.get_connection()
            conn.execute("""
                CREATE TABLE IF NOT EXISTS file_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    operation TEXT NOT NULL,
                    path TEXT NOT NULL,
                    details TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
        except Exception as e:
            logger.error(f"Failed to create file history: {e}")
    
    def create_file(self, path: str, content: str = ""):
        """Create a new file"""
        try:
            filepath = Path(path)
            
            if self.safety.is_protected_path(str(filepath.parent)):
                return {"status": "error", "message": "⛔ Cannot create in protected location"}
            
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self._save_history("create_file", str(filepath))
            logger.info(f"✅ File created: {filepath}")
            
            return {
                "status": "success",
                "message": f"File created: {filepath.name}",
                "data": {"path": str(filepath.absolute())}
            }
        except Exception as e:
            logger.error(f"Failed to create file: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def create_folder(self, path: str):
        """Create a new folder"""
        try:
            folderpath = Path(path)
            
            if self.safety.is_protected_path(str(folderpath.parent)):
                return {"status": "error", "message": "⛔ Cannot create in protected location"}
            
            folderpath.mkdir(parents=True, exist_ok=True)
            
            self._save_history("create_folder", str(folderpath))
            logger.info(f"✅ Folder created: {folderpath}")
            
            return {
                "status": "success",
                "message": f"Folder created: {folderpath.name}",
                "data": {"path": str(folderpath.absolute())}
            }
        except Exception as e:
            logger.error(f"Failed to create folder: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def delete(self, path: str, to_recycle_bin: bool = True):
        """Delete file or folder"""
        try:
            filepath = Path(path)
            
            # Safety check
            validation = self.safety.validate_operation(str(filepath), "delete")
            if not validation["safe"]:
                return {"status": "blocked", "message": validation["message"]}
            
            if to_recycle_bin:
                try:
                    from send2trash import send2trash
                    send2trash(str(filepath))
                    action = "moved to recycle bin"
                except ImportError:
                    if filepath.is_file():
                        filepath.unlink()
                    else:
                        shutil.rmtree(filepath)
                    action = "deleted permanently"
            else:
                if filepath.is_file():
                    filepath.unlink()
                else:
                    shutil.rmtree(filepath)
                action = "deleted permanently"
            
            self._save_history("delete", str(filepath), action)
            logger.info(f"✅ {filepath.name} {action}")
            
            return {
                "status": "success",
                "message": f"{filepath.name} {action}"
            }
        except Exception as e:
            logger.error(f"Failed to delete: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def rename(self, old_path: str, new_name: str):
        """Rename file or folder"""
        try:
            old = Path(old_path)
            
            validation = self.safety.validate_operation(str(old), "rename")
            if not validation["safe"]:
                return {"status": "blocked", "message": validation["message"]}
            
            new = old.parent / new_name
            old.rename(new)
            
            self._save_history("rename", str(old), f"→ {new_name}")
            logger.info(f"✅ Renamed: {old.name} → {new.name}")
            
            return {
                "status": "success",
                "message": f"Renamed to {new.name}",
                "data": {"old": str(old), "new": str(new)}
            }
        except Exception as e:
            logger.error(f"Failed to rename: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def move(self, source: str, destination: str):
        """Move file or folder"""
        try:
            src = Path(source)
            dest = Path(destination)
            
            validation = self.safety.validate_operation(str(src), "move")
            if not validation["safe"]:
                return {"status": "blocked", "message": validation["message"]}
            
            if self.safety.is_protected_path(str(dest)):
                return {"status": "blocked", "message": "⛔ Cannot move to protected location"}
            
            if dest.is_dir():
                dest = dest / src.name
            
            shutil.move(str(src), str(dest))
            
            self._save_history("move", str(src), f"→ {dest}")
            logger.info(f"✅ Moved: {src.name} → {dest}")
            
            return {
                "status": "success",
                "message": f"Moved {src.name}",
                "data": {"source": str(src), "destination": str(dest)}
            }
        except Exception as e:
            logger.error(f"Failed to move: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def copy(self, source: str, destination: str):
        """Copy file or folder"""
        try:
            src = Path(source)
            dest = Path(destination)
            
            validation = self.safety.validate_operation(str(src), "copy")
            if not validation["safe"]:
                return {"status": "blocked", "message": validation["message"]}
            
            if dest.is_dir():
                dest = dest / src.name
            
            if src.is_file():
                shutil.copy2(str(src), str(dest))
            else:
                shutil.copytree(str(src), str(dest))
            
            self._save_history("copy", str(src), f"→ {dest}")
            logger.info(f"✅ Copied: {src.name}")
            
            return {
                "status": "success",
                "message": f"Copied {src.name}",
                "data": {"source": str(src), "destination": str(dest)}
            }
        except Exception as e:
            logger.error(f"Failed to copy: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def get_info(self, path: str):
        """Get file/folder information"""
        try:
            filepath = Path(path)
            
            if not filepath.exists():
                return {"status": "error", "message": f"Path not found: {path}"}
            
            stats = filepath.stat()
            
            info = {
                "name": filepath.name,
                "path": str(filepath.absolute()),
                "type": "folder" if filepath.is_dir() else "file",
                "extension": filepath.suffix if filepath.is_file() else None,
                "size": self._format_size(stats.st_size),
                "created": datetime.fromtimestamp(stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
                "modified": datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
            }
            
            return {"status": "success", "data": info}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def open_location(self, path: str):
        """Open file location in Explorer"""
        try:
            filepath = Path(path).absolute()
            
            if not filepath.exists():
                return {"status": "error", "message": f"Path not found"}
            
            subprocess.run(['explorer', '/select,', str(filepath)])
            logger.info(f"Opened location: {filepath}")
            
            return {"status": "success", "message": f"Opened location"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _format_size(self, size_bytes: int) -> str:
        """Format bytes to human readable"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"
    
    def _save_history(self, operation: str, path: str, details: str = ""):
        """Save to history"""
        try:
            conn = self.db.get_connection()
            conn.execute(
                "INSERT INTO file_history (operation, path, details) VALUES (?, ?, ?)",
                (operation, path, details)
            )
            conn.commit()
        except:
            pass


class FileSearch:
    """File search operations"""
    
    def search_by_name(self, directory: str, filename: str, recursive: bool = True):
        """Search files by name"""
        try:
            dir_path = Path(directory)
            
            if not dir_path.exists():
                return {"status": "error", "message": f"Directory not found"}
            
            results = []
            pattern = f"*{filename}*"
            
            matches = dir_path.rglob(pattern) if recursive else dir_path.glob(pattern)
            
            for match in matches:
                if len(results) >= 50:
                    break
                results.append({
                    "name": match.name,
                    "path": str(match.absolute()),
                    "type": "folder" if match.is_dir() else "file"
                })
            
            logger.info(f"Found {len(results)} matches for '{filename}'")
            
            return {"status": "success", "results": results, "count": len(results)}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def search_by_extension(self, directory: str, extension: str):
        """Search by file extension"""
        try:
            dir_path = Path(directory)
            
            if not dir_path.exists():
                return {"status": "error", "message": "Directory not found"}
            
            if not extension.startswith('.'):
                extension = '.' + extension
            
            results = []
            
            for match in dir_path.rglob(f"*{extension}"):
                if len(results) >= 50:
                    break
                if match.is_file():
                    results.append({
                        "name": match.name,
                        "path": str(match.absolute())
                    })
            
            return {"status": "success", "results": results, "count": len(results)}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def search_recent(self, directory: str, days: int = 7):
        """Search recently modified files"""
        try:
            dir_path = Path(directory)
            
            if not dir_path.exists():
                return {"status": "error", "message": "Directory not found"}
            
            cutoff = time.time() - (days * 24 * 60 * 60)
            results = []
            
            for item in dir_path.rglob("*"):
                if item.is_file() and item.stat().st_mtime > cutoff:
                    if len(results) >= 50:
                        break
                    results.append({
                        "name": item.name,
                        "path": str(item.absolute()),
                        "modified": datetime.fromtimestamp(item.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
                    })
            
            results.sort(key=lambda x: x['modified'], reverse=True)
            
            return {"status": "success", "results": results, "count": len(results)}
        except Exception as e:
            return {"status": "error", "message": str(e)}


class FolderOrganizer:
    """Organize folders"""
    
    FILE_TYPES = {
        'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp'],
        'videos': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv'],
        'audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a'],
        'documents': ['.pdf', '.doc', '.docx', '.txt', '.xls', '.xlsx', '.ppt', '.pptx'],
        'archives': ['.zip', '.rar', '.7z', '.tar', '.gz'],
        'code': ['.py', '.js', '.java', '.cpp', '.c', '.html', '.css', '.php'],
    }
    
    def organize_by_type(self, directory: str):
        """Organize files by type"""
        try:
            dir_path = Path(directory)
            
            if not dir_path.exists():
                return {"status": "error", "message": "Directory not found"}
            
            if SafetyManager.is_protected_path(directory):
                return {"status": "blocked", "message": "⛔ Cannot organize protected folder"}
            
            organized = {}
            files = [f for f in dir_path.iterdir() if f.is_file()]
            
            for file in files:
                file_type = self._get_file_type(file.suffix.lower())
                
                subfolder = dir_path / file_type.capitalize()
                subfolder.mkdir(exist_ok=True)
                
                try:
                    shutil.move(str(file), str(subfolder / file.name))
                    organized[file_type] = organized.get(file_type, 0) + 1
                except Exception as e:
                    logger.warning(f"Failed to move {file.name}: {e}")
            
            total = sum(organized.values())
            logger.info(f"✅ Organized {total} files")
            
            return {
                "status": "success",
                "message": f"Organized {total} files",
                "data": organized
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def organize_by_date(self, directory: str):
        """Organize files by date (YYYY-MM)"""
        try:
            dir_path = Path(directory)
            
            if not dir_path.exists():
                return {"status": "error", "message": "Directory not found"}
            
            if SafetyManager.is_protected_path(directory):
                return {"status": "blocked", "message": "⛔ Cannot organize protected folder"}
            
            moved = 0
            files = [f for f in dir_path.iterdir() if f.is_file()]
            
            for file in files:
                mod_time = datetime.fromtimestamp(file.stat().st_mtime)
                folder_name = mod_time.strftime('%Y-%m')
                
                date_folder = dir_path / folder_name
                date_folder.mkdir(exist_ok=True)
                
                try:
                    shutil.move(str(file), str(date_folder / file.name))
                    moved += 1
                except:
                    pass
            
            logger.info(f"✅ Organized {moved} files by date")
            
            return {
                "status": "success",
                "message": f"Organized {moved} files by date"
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _get_file_type(self, extension: str) -> str:
        """Get file type from extension"""
        for file_type, extensions in self.FILE_TYPES.items():
            if extension in extensions:
                return file_type
        return 'others'


# ============================================================
# GLOBAL INSTANCES
# ============================================================

_file_manager = FileManager()
_file_search = FileSearch()
_organizer = FolderOrganizer()


# ============================================================
# CONVENIENCE FUNCTIONS
# ============================================================

# File/Folder operations
def create_file(path, content=""):
    return _file_manager.create_file(path, content)

def create_folder(path):
    return _file_manager.create_folder(path)

def delete(path, to_recycle_bin=True):
    return _file_manager.delete(path, to_recycle_bin)

def rename(old_path, new_name):
    return _file_manager.rename(old_path, new_name)

def move(source, destination):
    return _file_manager.move(source, destination)

def copy(source, destination):
    return _file_manager.copy(source, destination)

def get_info(path):
    return _file_manager.get_info(path)

def open_location(path):
    return _file_manager.open_location(path)

# Search
def search_by_name(directory, filename, recursive=True):
    return _file_search.search_by_name(directory, filename, recursive)

def search_by_extension(directory, extension):
    return _file_search.search_by_extension(directory, extension)

def search_recent(directory, days=7):
    return _file_search.search_recent(directory, days)

# Organize
def organize_by_type(directory):
    return _organizer.organize_by_type(directory)

def organize_by_date(directory):
    return _organizer.organize_by_date(directory)