import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

function Profile() {
  const navigate = useNavigate();

  const savedProfile = JSON.parse(
    localStorage.getItem("msmeProfile") || "null"
  );

  const [formData, setFormData] = useState(
    savedProfile || {
      businessName: "",
      ownerName: "",
      businessType: "",
      industry: "",
      location: "",
      employeeCount: "",
      annualTurnover: "",
      yearsInBusiness: "",
      currentTechnology: "",
    }
  );

  const [saved, setSaved] = useState(false);

  const handleChange = (event) => {
    const { name, value } = event.target;

    setFormData((previous) => ({
      ...previous,
      [name]: value,
    }));

    setSaved(false);
  };

  const handleSubmit = (event) => {
    event.preventDefault();

    localStorage.setItem(
      "msmeProfile",
      JSON.stringify(formData)
    );

    setSaved(true);
  };

  const handleContinue = () => {
    navigate("/assessment");
  };

  return (
    <div className="profile-page">
      <div className="profile-container">

        {/* Header */}
        <div className="profile-header">

          <div>
            <p className="assessment-label">
              MSME BUSINESS PROFILE
            </p>

            <h1>Tell Us About Your Business</h1>

            <p>
              Provide some basic information about your
              business. This information will help personalize
              your cloud maturity assessment.
            </p>
          </div>

          <Link
            to="/"
            className="secondary-button"
          >
            ← Home
          </Link>

        </div>

        {/* Form */}
        <form
          className="profile-form"
          onSubmit={handleSubmit}
        >

          {/* Business Information */}
          <section className="profile-section">

            <div className="profile-section-heading">
              <h2>Business Information</h2>

              <p>
                Basic information about your MSME.
              </p>
            </div>

            <div className="form-grid">

              <div className="form-group">
                <label htmlFor="businessName">
                  Business Name
                </label>

                <input
                  id="businessName"
                  name="businessName"
                  type="text"
                  placeholder="Enter business name"
                  value={formData.businessName}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="ownerName">
                  Owner / Manager Name
                </label>

                <input
                  id="ownerName"
                  name="ownerName"
                  type="text"
                  placeholder="Enter owner or manager name"
                  value={formData.ownerName}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="businessType">
                  Business Type
                </label>

                <select
                  id="businessType"
                  name="businessType"
                  value={formData.businessType}
                  onChange={handleChange}
                  required
                >
                  <option value="">
                    Select business type
                  </option>
                  <option value="Micro">
                    Micro
                  </option>
                  <option value="Small">
                    Small
                  </option>
                  <option value="Medium">
                    Medium
                  </option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="industry">
                  Industry
                </label>

                <select
                  id="industry"
                  name="industry"
                  value={formData.industry}
                  onChange={handleChange}
                  required
                >
                  <option value="">
                    Select industry
                  </option>
                  <option value="Manufacturing">
                    Manufacturing
                  </option>
                  <option value="Retail">
                    Retail
                  </option>
                  <option value="Agriculture">
                    Agriculture
                  </option>
                  <option value="Food Processing">
                    Food Processing
                  </option>
                  <option value="Textiles">
                    Textiles
                  </option>
                  <option value="Services">
                    Services
                  </option>
                  <option value="Other">
                    Other
                  </option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="location">
                  Business Location
                </label>

                <input
                  id="location"
                  name="location"
                  type="text"
                  placeholder="City / District / State"
                  value={formData.location}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="employeeCount">
                  Number of Employees
                </label>

                <input
                  id="employeeCount"
                  name="employeeCount"
                  type="number"
                  min="1"
                  placeholder="e.g. 25"
                  value={formData.employeeCount}
                  onChange={handleChange}
                  required
                />
              </div>

            </div>

          </section>

          {/* Business Scale */}
          <section className="profile-section">

            <div className="profile-section-heading">
              <h2>Business Scale</h2>

              <p>
                Help us understand your organization's size
                and experience.
              </p>
            </div>

            <div className="form-grid">

              <div className="form-group">
                <label htmlFor="annualTurnover">
                  Annual Turnover
                </label>

                <select
                  id="annualTurnover"
                  name="annualTurnover"
                  value={formData.annualTurnover}
                  onChange={handleChange}
                  required
                >
                  <option value="">
                    Select turnover range
                  </option>
                  <option value="Below 10 Lakhs">
                    Below ₹10 Lakhs
                  </option>
                  <option value="10-50 Lakhs">
                    ₹10–50 Lakhs
                  </option>
                  <option value="50 Lakhs-1 Crore">
                    ₹50 Lakhs–₹1 Crore
                  </option>
                  <option value="1-5 Crores">
                    ₹1–5 Crores
                  </option>
                  <option value="Above 5 Crores">
                    Above ₹5 Crores
                  </option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="yearsInBusiness">
                  Years in Business
                </label>

                <input
                  id="yearsInBusiness"
                  name="yearsInBusiness"
                  type="number"
                  min="0"
                  placeholder="e.g. 8"
                  value={formData.yearsInBusiness}
                  onChange={handleChange}
                  required
                />
              </div>

            </div>

          </section>

          {/* Technology */}
          <section className="profile-section">

            <div className="profile-section-heading">
              <h2>Current Technology</h2>

              <p>
                Tell us about your current digital
                infrastructure.
              </p>
            </div>

            <div className="form-group">

              <label htmlFor="currentTechnology">
                How would you describe your current
                technology usage?
              </label>

              <select
                id="currentTechnology"
                name="currentTechnology"
                value={formData.currentTechnology}
                onChange={handleChange}
                required
              >
                <option value="">
                  Select an option
                </option>

                <option value="Mostly manual">
                  Mostly manual processes
                </option>

                <option value="Basic digital tools">
                  Basic digital tools
                </option>

                <option value="Multiple digital systems">
                  Multiple digital systems
                </option>

                <option value="Cloud-based systems">
                  Cloud-based systems
                </option>

                <option value="Highly integrated cloud">
                  Highly integrated cloud environment
                </option>
              </select>

            </div>

          </section>

          {/* Actions */}
          <div className="profile-actions">

            <Link
              to="/"
              className="secondary-button"
            >
              Cancel
            </Link>

            <button
              type="submit"
              className="primary-button"
            >
              Save Profile
            </button>

          </div>

          {saved && (
            <div className="profile-success">
              ✓ Profile saved successfully.
            </div>
          )}

        </form>

        {/* Continue */}
        {saved && (
          <div className="continue-assessment">

            <div>
              <h3>Ready for the assessment?</h3>

              <p>
                Your business profile has been saved.
                Continue to assess your cloud maturity.
              </p>
            </div>

            <button
              type="button"
              className="primary-button"
              onClick={handleContinue}
            >
              Start Assessment →
            </button>

          </div>
        )}

      </div>
    </div>
  );
}

export default Profile;