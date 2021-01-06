import FileType from '@/components/types/file';

export interface RespType {
  // Server status code
  status_code: number;
  // Server response message
  msg: string;
  // File list data
  data?: FileType[];
}

export default RespType;
