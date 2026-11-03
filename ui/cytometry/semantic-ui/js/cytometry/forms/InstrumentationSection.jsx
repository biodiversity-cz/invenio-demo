import React from "react";
import { TextField } from "@js/oarepo_ui/forms";
import { i18next } from "@translations/i18next";

export const InstrumentationSection = {
  key: "instrumentation",
  label: i18next.t("Instrumentation"),
  component: () => (
    <>
      <TextField
        fieldPath="metadata.instrumentation.instrument_affiliation"
        label={i18next.t("Instrument affiliation")}
        required
      />
      <TextField
        fieldPath="metadata.instrumentation.manufacturer"
        label={i18next.t("Manufacturer")}
      />
      <TextField
        fieldPath="metadata.instrumentation.model"
        label={i18next.t("Model")}
        required
      />
      <TextField
        fieldPath="metadata.instrumentation.instrument_id"
        label={i18next.t("Instrument ID")}
      />
      <TextField
        fieldPath="metadata.instrumentation.light_source"
        label={i18next.t("Light source")}
        required
      />
      <TextField
        fieldPath="metadata.instrumentation.channel_name_standard_position"
        label={i18next.t("Channel name (standard position)")}
      />
    </>
  ),
  includesPaths: [
    "metadata.instrumentation.instrument_affiliation",
    "metadata.instrumentation.manufacturer",
    "metadata.instrumentation.model",
    "metadata.instrumentation.instrument_id",
    "metadata.instrumentation.light_source",
    "metadata.instrumentation.channel_name_standard_position",
  ],
};
