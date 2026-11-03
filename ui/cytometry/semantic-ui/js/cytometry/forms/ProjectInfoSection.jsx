import React from "react";
import { TextField, StringArrayField } from "@js/oarepo_ui/forms";
import { i18next } from "@translations/i18next";
import { PersonArrayField } from "./PersonArrayField";

export const ProjectInfoSection = {
  key: "project_info",
  label: i18next.t("Project information"),
  component: () => (
    <>
      <TextField
        fieldPath="metadata.project_info.project_title"
        label={i18next.t("Project title")}
        required
      />
      <TextField
        fieldPath="metadata.project_info.project_description"
        label={i18next.t("Project description")}
        required
        optimized
      />
      <PersonArrayField
        fieldPath="metadata.project_info.authors"
        label={i18next.t("Project authors")}
        addButtonLabel={i18next.t("Add author")}
        removeButtonLabel={i18next.t("Remove author")}
        required
      />
      <StringArrayField
        fieldPath="metadata.project_info.publication_doi"
        label={i18next.t("Publication DOI")}
        addButtonLabel={i18next.t("Add DOI")}
      />
      <TextField
        fieldPath="metadata.project_info.funding"
        label={i18next.t("Funding")}
        optimized
      />
    </>
  ),
  includesPaths: [
    "metadata.project_info.project_title",
    "metadata.project_info.project_description",
    "metadata.project_info.authors",
    "metadata.project_info.publication_doi",
    "metadata.project_info.funding",
  ],
};
