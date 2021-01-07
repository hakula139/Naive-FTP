export interface FileType {
  // File name
  fileName: string;
  // File size
  fileSize: string;
  // File type
  fileType: string;
  // Last modified time
  modTime: string;
  // Permissions
  perms: string;
  // Owner
  owner: string;
}

export default FileType;
