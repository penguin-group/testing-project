import publicWidget from "@web/legacy/js/public/public_widget";
import core from "@web/core/core";
import _t from core._t;


publicWidget.registry.CertificatePortalForm = publicWidget.Widget.extend({
    selector: '.portal-certificate-form',
    events: {
        'change #purchase_order_id': '_onPurchaseOrderChange',
        'click #add_line_btn': '_onAddLine',
        'click .remove-line': '_onRemoveLine',
        'change .product-select': '_onProductChange',
        'submit #certificate_form': '_onFormSubmit',
    },

    init: function () {
        this._super.apply(this, arguments);
        this.lineCounter = 0;
        this.availableProducts = [];
    },

    /**
     * Handle purchase order selection change
     */
    _onPurchaseOrderChange: function (ev) {
        var self = this;
        var poId = $(ev.currentTarget).val();
        
        if (poId) {
            this._loadPurchaseOrderProducts(poId).then(function (products) {
                self.availableProducts = products;
                self.$('#add_line_btn').prop('disabled', false);
                self.$('#certificate_lines_container').html('<p class="text-muted">Click "Add Line" to add certificate lines.</p>');
            }).catch(function (error) {
                self._showError('Error loading products: ' + error);
            });
        } else {
            this.$('#add_line_btn').prop('disabled', true);
            this.$('#certificate_lines_container').html('<p class="text-muted">Select a purchase order first to add certificate lines.</p>');
            this.availableProducts = [];
        }
    },

    /**
     * Load products for selected purchase order
     */
    _loadPurchaseOrderProducts: function (poId) {
        return new Promise((resolve, reject) => {
            $.ajax({
                url: '/my/certificate/get_po_products',
                type: 'POST',
                dataType: 'json',
                contentType: 'application/json',
                data: JSON.stringify({
                    jsonrpc: '2.0',
                    method: 'call',
                    params: {purchase_order_id: parseInt(poId)}
                }),
                success: function(response) {
                    if (response.result && !response.result.error) {
                        resolve(response.result.products);
                    } else {
                        reject(response.result.error || 'Unknown error');
                    }
                },
                error: function(xhr, status, error) {
                    reject(error || 'Network error');
                }
            });
        });
    },

    /**
     * Add new certificate line
     */
    _onAddLine: function (ev) {
        ev.preventDefault();
        
        if (this.availableProducts.length === 0) {
            this._showError('No products available for the selected purchase order');
            return;
        }

        var $newLine = this._createNewLine();
        
        if (this.$('#certificate_lines_container p').length) {
            this.$('#certificate_lines_container').empty();
        }
        
        this.$('#certificate_lines_container').append($newLine);
        this._updateFormValidation();
    },

    /**
     * Create new certificate line HTML
     */
    _createNewLine: function () {
        var lineId = 'line_' + (++this.lineCounter);
        var $template = this.$('#line_template');
        var $newLine = $($template.html());
        
        $newLine.attr('data-line-id', lineId);
        
        // Populate products dropdown
        var $productSelect = $newLine.find('.product-select');
        $productSelect.attr('id', lineId + '_product');
        
        this.availableProducts.forEach(function (product) {
            $productSelect.append($('<option>', {
                value: product.id,
                text: product.name
            }));
        });

        // Set unique IDs for form elements
        $newLine.find('.description-field').attr('id', lineId + '_description');
        $newLine.find('.qty-field').attr('id', lineId + '_qty');
        $newLine.find('.date-field').attr('id', lineId + '_date');

        return $newLine;
    },

    /**
     * Remove certificate line
     */
    _onRemoveLine: function (ev) {
        ev.preventDefault();
        
        $(ev.currentTarget).closest('.certificate-line').remove();
        
        if (this.$('#certificate_lines_container .certificate-line').length === 0) {
            this.$('#certificate_lines_container').html('<p class="text-muted">Click "Add Line" to add certificate lines.</p>');
        }
        
        this._updateFormValidation();
    },

    /**
     * Handle product selection change
     */
    _onProductChange: function (ev) {
        var productId = $(ev.currentTarget).val();
        var $line = $(ev.currentTarget).closest('.certificate-line');
        
        var product = this.availableProducts.find(p => p.id == productId);
        if (product && product.description) {
            $line.find('.description-field').val(product.description);
        }
    },

    /**
     * Handle form submission
     */
    _onFormSubmit: function (ev) {
        var self = this;
        
        // Collect certificate lines data
        var lines = [];
        this.$('.certificate-line').each(function () {
            var $line = $(this);
            var line = {
                product_id: $line.find('.product-select').val(),
                description: $line.find('.description-field').val(),
                qty_received: $line.find('.qty-field').val(),
                date_received: $line.find('.date-field').val()
            };
            
            if (line.product_id && line.qty_received) {
                lines.push(line);
            }
        });
        
        // Validate that we have at least one line
        if (lines.length === 0) {
            this._showError('Please add at least one certificate line.');
            ev.preventDefault();
            return false;
        }
        
        // Set the data in hidden field
        this.$('#certificate_lines_data').val(JSON.stringify(lines));
        
        // Show loading state
        this._setLoadingState(true);
    },

    /**
     * Update form validation state
     */
    _updateFormValidation: function () {
        var hasLines = this.$('.certificate-line').length > 0;
        var $submitBtn = this.$('button[type="submit"]');
        
        if (hasLines) {
            $submitBtn.prop('disabled', false);
        } else {
            $submitBtn.prop('disabled', true);
        }
    },

    /**
     * Show error message
     */
    _showError: function (message) {
        // Remove existing alerts
        this.$('.alert-danger').remove();
        
        // Add new alert
        var $alert = $('<div class="alert alert-danger alert-dismissible" role="alert">' +
            '<button type="button" class="close" data-dismiss="alert" aria-label="Close">' +
            '<span aria-hidden="true">&times;</span>' +
            '</button>' +
            '<strong>Error:</strong> ' + message +
            '</div>');
        
        this.$('.card').first().prepend($alert);
        
        // Auto-dismiss after 5 seconds
        setTimeout(function () {
            $alert.fadeOut();
        }, 5000);
    },

    /**
     * Set loading state
     */
    _setLoadingState: function (loading) {
        if (loading) {
            this.$el.addClass('loading');
            this.$('button[type="submit"]')
                .prop('disabled', true)
                .html('<i class="fa fa-spinner fa-spin"></i> Submitting...');
        } else {
            this.$el.removeClass('loading');
            this.$('button[type="submit"]')
                .prop('disabled', false)
                .html('Submit Certificate');
        }
    },
});

// Initialize date fields with today's date
$(document).ready(function () {
    var today = new Date().toISOString().split('T')[0];
    $('#date').val(today);
    
    // Set default date for new lines
    $(document).on('focus', '.date-field', function () {
        if (!$(this).val()) {
            $(this).val(today);
        }
    });

    // This will manually attach the widget to all matching elements
    if ($('.portal-certificate-form').length) {
        publicWidget.registry.CertificatePortalForm.attachTo('.portal-certificate-form');
    }
});

return publicWidget.registry.CertificatePortalForm;
