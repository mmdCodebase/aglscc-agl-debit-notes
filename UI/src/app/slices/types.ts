// Email
export type Email = {
  email_id: string;
  file_name: string;
};

export type FetchEmailsResponse = Email[];

export type EmailSliceState = {
  emails: Email[];
  status: "idle" | "succeeded" | "failed" | "loading";
  error: string | null;
  emailIndex: number;
};

// File
export type FileResponse = Blob | null;
export type CWUploadResponse = {
  blob: Blob;
  filename: string;
};

export type FileSliceState = {
  pdfBlob: Blob | null;
  pdfStatus: "idle" | "succeeded" | "failed" | "loading";
  pdfError: string | null;
  cwUpload: CWUploadResponse | null;
  downloadCWStatus: "idle" | "succeeded" | "failed" | "loading";
  downloadCWError: string | null;
};

// Data
export type Charge = {
  id?: number | null;
  charge_code: string;
  description?: string;
  charges_in_usd?: number;
};

export type FetchDataResponse = {
  debit_note_id?: number;
  agl_shipment_number?: string;
  creditor?: string;
  invoice_num?: string;
  invoice_date?: Date;
  supplier_cost_ref?: string;
  ar_ap?: string;
  is_post?: string;
  charges?: Charge[];
  subject?: string;
  email_id?: string;
};

export type CWDataResponse = {
  email_id: string;
  agl_shipment_number?: string;
  creditor?: string;
  invoice_num?: string;
  invoice_date?: Date;
  supplier_cost_ref: string;
  ar_ap?: string;
  is_post?: string;
  updated_at?: Date;
  FRT?: number;
  AGEN?: number;
  AMS?: number;
  EQUIP?: number;
  ORIGIN?: number;
  LOCAL?: number;
  PP?: number;
  TERFEE?: number;
  TELEX?: number;
  VGM?: number;
  DCART?: number;
  SEAL?: number;
  DOC?: number;
  BOOK?: number;
  CCLR?: number;
  ALINE?: number;
  PSEC?: number;
  EGF?: number;
  TRANS?: number;
  CHRENT?: number;
};

export type DataSliceState = {
  data: FetchDataResponse;
  dataStatus: "idle" | "succeeded" | "failed" | "loading";
  dataError: string | null;
  cwUploadData: CWDataResponse[];
  cwUploadDataStatus: "idle" | "succeeded" | "failed" | "loading";
  cwUploadDataError: string | null;
};

// Action
export type ActionResponse = {
  message: string;
};

export type ActionSliceState = {
  skipAction: ActionResponse | null;
  skipActionStatus: "idle" | "succeeded" | "failed" | "loading";
  skipActionError: string | null;
  saveAction: ActionResponse | null;
  saveActionStatus: "idle" | "succeeded" | "failed" | "loading";
  saveActionError: string | null;
};
