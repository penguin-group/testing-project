odoo.define('website_salary_attachment_request.sa_form', [], function (require) {
    'use strict';
  
    function jsonRpc(url, params) {
      return fetch(url, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          jsonrpc: '2.0',
          method: 'call',
          params: params || {},
        }),
      })
        .then(function (response) { return response.json(); })
        .then(function (payload) {
          if (payload && Object.prototype.hasOwnProperty.call(payload, 'result')) {
            return payload.result;
          }
          var error = (payload && payload.error && payload.error.data && payload.error.data.message) ||
            (payload && payload.error && payload.error.message) ||
            'Unknown server error';
          throw new Error(error);
        });
    }
  
    function init() {
      const msg = document.getElementById('sa_msg');
      const empIdInput = document.getElementById('sa_emp_id');
      const nameInput = document.getElementById('sa_emp_name');
      const idnumInput = document.getElementById('sa_emp_idnum');
      const addrInput = document.getElementById('sa_emp_address');
      const descInput = document.getElementById('sa_desc');
      const form = document.getElementById('salaryAttachmentForm');
      const successBox = document.getElementById('sa_success');
      if (!form) { return; }
      let translations = {
        load_error: 'Unable to load employee data.',
        network_error: 'Network error while loading employee information.',
        submitting: 'Submitting...',
        submit_success: 'Request submitted. ID: %s',
        submit_error: 'The request could not be submitted.',
        submit_network_error: 'Network or server error.',
        requested_amount_label: 'Requested Amount (%s) *',
        amount_helper: 'You can request up to %s.',
      };

      function format(template, value) {
        if (typeof template !== 'string') {
          return value;
        }
        return template.includes('%s') ? template.replace('%s', value) : `${template} ${value}`;
      }
  
      // Load defaults
      console.log('[SA-Form] requesting defaults...');
      jsonRpc('/salary-attachment/defaults', {})
        .then(function (data) {
          console.log('[SA-Form] defaults response:', data);
          if (!data || !data.ok) {
            msg.textContent = (data && data.error) || translations.load_error;
            return;
          }
          if (data.translations) {
            translations = Object.assign({}, translations, data.translations);
          }
          empIdInput.value = data.employee_id;
          nameInput.value = data.employee_name || '';
          idnumInput.value = data.employee_identification_id || '';
          addrInput.value = data.employee_work_address || '';
          var currencyDisplay = data.contract_currency_symbol || data.contract_currency_code || '';
          if (currencyDisplay) {
            var amountLabel = document.getElementById('sa_amount_label');
            var amountInput = document.getElementById('sa_amount');
            if (amountLabel) {
              amountLabel.textContent = format(translations.requested_amount_label, currencyDisplay);
            }
            if (amountInput) {
              amountInput.setAttribute('placeholder', '0.00 ' + currencyDisplay);
              amountInput.setAttribute('step', '0.01');
              amountInput.setAttribute('min', '0.01');
            }
          }
          const amountHint = document.getElementById('sa_amount_hint');
          if (amountHint) {
            if (data.max_amount_display) {
              amountHint.textContent = format(translations.amount_helper, data.max_amount_display);
            } else {
              amountHint.textContent = '';
            }
          }
        })
        .catch(function (err) {
          console.error('[SA-Form] defaults error:', err);
          msg.textContent = translations.network_error;
        });
  
      // Submit
      form.addEventListener('submit', function (e) {
        e.preventDefault();
        if (successBox) {
          successBox.classList.add('d-none');
          successBox.textContent = '';
        }
        msg.textContent = translations.submitting;
        msg.classList.remove('text-success', 'text-danger', 'd-none');
  
        const checked = document.querySelector('input[name="frequency"]:checked');
        const payload = {
          employee_id: empIdInput.value,
          amount: document.getElementById('sa_amount').value,
          description: descInput ? descInput.value : '',
          frequency: checked ? checked.value : null,
        };
  
        console.log('[SA-Form] submitting payload:', payload);
        jsonRpc('/salary-attachment/submit', payload)
          .then(function (res) {
            console.log('[SA-Form] submit response:', res);
            if (res && res.ok) {
              msg.textContent = '';
              msg.classList.add('d-none');
              if (form) {
                form.classList.add('d-none');
              }
              if (successBox) {
                successBox.textContent = format(translations.submit_success, res.id);
                successBox.classList.remove('d-none');
              }
            } else {
              msg.classList.remove('text-success');
              msg.classList.add('text-danger');
              msg.textContent = (res && res.error) || translations.submit_error;
            }
          })
          .catch(function (err) {
            console.error('[SA-Form] submit error:', err);
            msg.classList.remove('text-success');
            msg.classList.add('text-danger');
            msg.textContent = translations.submit_network_error;
            if (successBox) {
              successBox.classList.add('d-none');
              successBox.textContent = '';
            }
          });
      });
    }
  
    // DOM listo
    if (document.readyState !== 'loading') {
      init();
    } else {
      document.addEventListener('DOMContentLoaded', init);
    }
  });
  