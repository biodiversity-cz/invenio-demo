import React from "react";
import { TextField } from "@js/oarepo_ui/forms";
import { i18next } from "@translations/i18next";

export const PreparationSection = {
  key: "preparation_and_standard",
  label: i18next.t("Preparation and standard"),
  component: () => (
    <>
      <TextField
        fieldPath="metadata.preparation_and_standard.isolation_buffer"
        label={i18next.t("Isolation buffer")}
      />
      <TextField
        fieldPath="metadata.preparation_and_standard.buffer_additives"
        label={i18next.t("Buffer additives")}
        optimized
      />
      <TextField
        fieldPath="metadata.preparation_and_standard.fluorochrome"
        label={i18next.t("Fluorochrome")}
      />
      <TextField
        fieldPath="metadata.preparation_and_standard.internal_standard_species"
        label={i18next.t("Internal standard species")}
      />
      <TextField
        fieldPath="metadata.preparation_and_standard.internal_standard_material"
        label={i18next.t("Internal standard material")}
      />
      <TextField
        fieldPath="metadata.preparation_and_standard.standard_c_value_pg"
        label={i18next.t("Standard C-value (pg)")}
      />
      <TextField
        fieldPath="metadata.preparation_and_standard.standard_c_value_citation"
        label={i18next.t("Standard C-value citation")}
        optimized
      />
    </>
  ),
  includesPaths: [
    "metadata.preparation_and_standard.isolation_buffer",
    "metadata.preparation_and_standard.buffer_additives",
    "metadata.preparation_and_standard.fluorochrome",
    "metadata.preparation_and_standard.internal_standard_species",
    "metadata.preparation_and_standard.internal_standard_material",
    "metadata.preparation_and_standard.standard_c_value_pg",
    "metadata.preparation_and_standard.standard_c_value_citation",
  ],
};
