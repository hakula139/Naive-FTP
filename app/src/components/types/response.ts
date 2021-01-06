import FileType from '@/components/types/file';

export interface RespType {
  // Operation result
  msg?: string;
  // File list data
  data?: FileType[];
}

export default RespType;
