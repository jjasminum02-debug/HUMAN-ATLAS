import manifest from '../../../../atlas-data/anatomy/skin/at10-appearance-v1/material.json';
import color from '../../../../atlas-data/anatomy/skin/at10-appearance-v1/color.webp?url';
import normal from '../../../../atlas-data/anatomy/skin/at10-appearance-v1/normal.webp?url';
import roughness from '../../../../atlas-data/anatomy/skin/at10-appearance-v1/roughness.webp?url';
import type { SkinMaterialPackage } from './skinMaterial.ts';
/** DEV candidate only. Does not populate registeredSkin or upgrade any fit/rights gate. */
export function skinAppearanceReviewFor(binding:typeof manifest=manifest):SkinMaterialPackage {return {...binding,maps:{
  color:{...binding.maps.color,url:color},normal:{...binding.maps.normal,url:normal},roughness:{...binding.maps.roughness,url:roughness},
}};}
export const skinAppearanceReview=skinAppearanceReviewFor();
