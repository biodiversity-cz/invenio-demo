import React from "react";
import { TextField } from "@js/oarepo_ui/forms";
import { FieldLabel } from "react-invenio-forms";
import { useFormikContext, getIn, FieldArray } from "formik";
import { Form, Icon, Button } from "semantic-ui-react";
import { i18next } from "@translations/i18next";

/**
 * Array of Person objects: { fullname, orcid, affiliation }.
 */
export function PersonArrayField({
  fieldPath,
  label,
  addButtonLabel,
  removeButtonLabel,
  required = false,
}) {
  const { values } = useFormikContext();

  return (
    <Form.Field required={required}>
      <FieldLabel htmlFor={fieldPath} label={label} />
      <FieldArray
        name={fieldPath}
        render={(arrayHelpers) => {
          const people = getIn(values, fieldPath, []);
          return (
            <>
              {people.map((item, index) => {
                const base = `${fieldPath}.${index}`;
                const isLast = index === people.length - 1;
                return (
                  <div
                    // eslint-disable-next-line react/no-array-index-key
                    key={index}
                    className="person-array-entry"
                  >
                    <TextField
                      fieldPath={`${base}.fullname`}
                      label={i18next.t("Full name")}
                      required
                      width={16}
                    />
                    <TextField
                      fieldPath={`${base}.orcid`}
                      label={i18next.t("ORCID")}
                      width={16}
                    />
                    <TextField
                      fieldPath={`${base}.affiliation`}
                      label={i18next.t("Affiliation")}
                      width={16}
                    />
                    <Form.Field>
                      <Button.Group>
                        <Button
                          aria-label={removeButtonLabel}
                          className="close-btn"
                          type="button"
                          icon
                          labelPosition="left"
                          onClick={() => arrayHelpers.remove(index)}
                        >
                          <Icon name="close" />
                          {removeButtonLabel}
                        </Button>
                        {isLast ? (
                          <Button
                            className="array-field-add-button"
                            type="button"
                            icon
                            labelPosition="left"
                            onClick={() => arrayHelpers.push({})}
                          >
                            <Icon name="add" />
                            {addButtonLabel}
                          </Button>
                        ) : null}
                      </Button.Group>
                    </Form.Field>
                  </div>
                );
              })}
              {people.length === 0 ? (
                <Form.Button
                  className="array-field-add-button inline"
                  type="button"
                  icon
                  labelPosition="left"
                  onClick={() => arrayHelpers.push({})}
                >
                  <Icon name="add" />
                  {addButtonLabel}
                </Form.Button>
              ) : null}
            </>
          );
        }}
      />
    </Form.Field>
  );
}
