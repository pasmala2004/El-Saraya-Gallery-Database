import api from '../lib/api';
import { Product, ProductCategory, PaginatedResponse } from '../types';

export const productsApi = {
  getAll: async (params?: {
    limit?: number;
    offset?: number;
    category_id?: string;
    active?: boolean;
    name?: string;
  }) => {
    const { data } = await api.get<PaginatedResponse<Product>>('/products', { params });
    return data;
  },

  getById: async (id: string) => {
    const { data } = await api.get<Product>(`/products/${id}`);
    return data;
  },

  create: async (product: Partial<Product>) => {
    const { data } = await api.post<Product>('/products', product);
    return data;
  },

  update: async (id: string, product: Partial<Product>) => {
    const { data } = await api.put<Product>(`/products/${id}`, product);
    return data;
  },

  delete: async (id: string) => {
    await api.delete(`/products/${id}`);
  },
};

export const categoriesApi = {
  getAll: async (params?: {
    limit?: number;
    offset?: number;
    name?: string;
  }) => {
    const { data } = await api.get<PaginatedResponse<ProductCategory>>('/product-categories', { params });
    return data;
  },

  getById: async (id: string) => {
    const { data } = await api.get<ProductCategory>(`/product-categories/${id}`);
    return data;
  },

  create: async (category: Partial<ProductCategory>) => {
    const { data } = await api.post<ProductCategory>('/product-categories', category);
    return data;
  },

  update: async (id: string, category: Partial<ProductCategory>) => {
    const { data } = await api.put<ProductCategory>(`/product-categories/${id}`, category);
    return data;
  },

  delete: async (id: string) => {
    await api.delete(`/product-categories/${id}`);
  },
};
