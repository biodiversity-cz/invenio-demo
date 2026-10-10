import React from "react";
import { TextField } from "@js/oarepo_ui/forms";
import { i18next } from "@translations/i18next";

export const InstrumentationSection = {
  key: "instrumentation",
  label: i18next.t("Instrumentation"),
  component: () => (
    <>
      <TextField
        fieldPath="metadata.instrumentation.manufacturer"
        label={i18next.t("Manufacturer")}
      />
      <TextField
        fieldPath="metadata.instrumentation.model"
        label={i18next.t("Model")}
      />
      <TextField
        fieldPath="metadata.instrumentation.instrument_id"
        label={i18next.t("Instrument ID")}
      />
      <TextField
        fieldPath="metadata.instrumentation.light_source"
        label={i18next.t("Light source")}
      />
    </>
  ),
  includesPaths: [
    "metadata.instrumentation.manufacturer",
    "metadata.instrumentation.model",
    "metadata.instrumentation.instrument_id",
    "metadata.instrumentation.light_source",
  ],
};
