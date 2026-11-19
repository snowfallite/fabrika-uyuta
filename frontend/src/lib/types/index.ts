// The only place to import API types from (tech.md, 10.3).
import type { components } from './api';
type S = components['schemas'];
export type ImageAsset = S['ImageAsset'];
export type SocialLink = S['SocialLink'];
export type ProductOption = S['ProductOption'];
export type SiteSettings = S['SiteSettings'];
export type CategorySummary = S['CategorySummary'];
export type CategoryDetail = S['CategoryDetail'];
export type GalleryItem = S['GalleryItem'];
export type HomeSlots = S['HomeSlots'];
export type HomeContent = S['HomeContent'];
export type LeadCreateRequest = S['LeadCreateRequest'];
export type LeadCreated = S['LeadCreated'];
export type CategorySlug = string; // v14: categories are editable data, the schema has no enum
