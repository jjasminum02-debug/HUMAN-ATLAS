import manifest from '../../../../atlas-data/anatomy/skin/at10-appearance-v1/material.json';
import color from '../../../../atlas-data/anatomy/skin/at10-appearance-v1/color.webp?url';
import normal from '../../../../atlas-data/anatomy/skin/at10-appearance-v1/normal.webp?url';
import roughness from '../../../../atlas-data/anatomy/skin/at10-appearance-v1/roughness.webp?url';
import type { SkinMaterialPackage } from './skinMaterial.ts';
/** DEV candidate only. Does not populate registeredSkin or upgrade any fit/rights gate. */
export const skinAppearanceReview:SkinMaterialPackage={...manifest,maps:{
  color:{...manifest.maps.color,url:color},normal:{...manifest.maps.normal,url:normal},roughness:{...manifest.maps.roughness,url:roughness},
}};
