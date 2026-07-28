export type ResponseEnvelope<T> = {
  data: T;
  meta?: PaginationMeta | Record<string, unknown> | null;
  errors?: string[] | null;
};

export type PaginationMeta = {
  page: number;
  per_page: number;
  total: number;
  total_pages: number;
};

export type User = {
  uuid: string;
  email: string;
  first_name: string;
  last_name: string;
  phone?: string | null;
  avatar_url?: string | null;
  is_active: boolean;
  is_verified: boolean;
  roles: string[];
};

export type CompanyAddress = {
  street: string;
  city: string;
  province: string;
  postal_code: string;
  country: string;
};

export type CompanySettings = {
  uuid?: string;
  company_name: string;
  trading_name?: string | null;
  registration_number?: string | null;
  vat_number?: string | null;
  email?: string | null;
  phone?: string | null;
  website?: string | null;
  address: CompanyAddress;
  logo_url?: string | null;
};

export type DashboardMetric = {
  label: string;
  value: string | number;
  change_percent?: number | null;
  trend?: string | null;
};

export type DashboardChartPoint = {
  month: string;
  revenue: string | number;
  expenses: string | number;
  profit: string | number;
};

export type DashboardActivityItem = {
  uuid: string;
  action: string;
  entity_type: string;
  description: string;
  user_name?: string | null;
  created_at: string;
};

export type Dashboard = {
  metrics: DashboardMetric[];
  charts: DashboardChartPoint[];
  activity: DashboardActivityItem[];
  quick_actions: string[];
};

export type Client = {
  uuid: string;
  client_number: string;
  company_name: string;
  trading_name?: string | null;
  email?: string | null;
  phone?: string | null;
  status: string;
  credit_limit: string | number;
  created_at: string;
  updated_at: string;
};

export type Product = {
  uuid: string;
  sku: string;
  barcode?: string | null;
  name: string;
  category_name?: string | null;
  purchase_price: string | number;
  selling_price: string | number;
  min_stock_level: number;
  current_stock: number;
  is_low_stock: boolean;
  is_active: boolean;
  unit_of_measure: string;
  created_at: string;
  updated_at: string;
};

export type StockAddition = {
  product_uuid: string;
  warehouse_name: string;
  quantity_before: number;
  quantity_added: number;
  quantity_after: number;
};

export type SupplierContact = {
  uuid?: string; full_name: string; job_title?: string | null; department?: string | null;
  email?: string | null; phone?: string | null; alternative_phone?: string | null;
  preferred_contact_method: 'email' | 'phone' | 'sms'; is_primary: boolean; notes?: string | null;
};

export type Supplier = {
  uuid: string; name: string; code: string; contact_person?: string | null;
  contact_email?: string | null; phone?: string | null; city?: string | null;
  country?: string | null; is_active: boolean; contact_count?: number;
  created_at: string; updated_at: string;
};

export type SupplierCreate = {
  name: string; code: string; contact_person?: string; contact_email?: string;
  phone?: string; city?: string; country?: string; payment_terms_days: number;
  lead_time_days: number; is_active: boolean; contacts: SupplierContact[];
};

export type PPECompliance = {
  total_issued: number;
  overdue_replacements: number;
  due_this_month: number;
  compliance_rate: number;
};

export type PPEItem = {
  uuid: string;
  name: string;
  category_name: string;
  size?: string | null;
  standard?: string | null;
  replacement_interval_days: number;
  current_stock: number;
  status: string;
  created_at: string;
  updated_at: string;
};

export type PPEIssue = {
  uuid: string;
  employee_name: string;
  employee_number: string;
  ppe_item_name: string;
  ppe_category: string;
  issued_date: string;
  replacement_due_date?: string | null;
  quantity: number;
  condition: string;
  status: string;
  is_overdue: boolean;
  created_at: string;
  updated_at: string;
};
