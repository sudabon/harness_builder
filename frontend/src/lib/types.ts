export type AnswerValue = string | string[];
export type AnswerMap = Record<string, AnswerValue>;

export interface User {
  id: string;
  email: string;
  created_at: string;
}

export interface Preset {
  id: string;
  name: string;
  description: string;
  answers: AnswerMap;
}

export interface Project {
  id: string;
  name: string;
  preset_id: string | null;
  answers: AnswerMap;
  created_at: string;
  updated_at: string;
}

export interface GeneratedFileSummary {
  id: string;
  file_path: string;
  is_edited: boolean;
  created_at: string;
  updated_at: string;
}

export interface GeneratedFilesList {
  items: GeneratedFileSummary[];
}

export interface GeneratedFile extends GeneratedFileSummary {
  content: string;
}
