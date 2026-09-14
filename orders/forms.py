from django import forms


class CheckoutForm(forms.Form):
    PAYMENT_CHOICES = (
        ('debit', 'Debit card'),
        ('wallet', 'Wallet card'),
        ('cod', 'Cash on delivery'),
    )

    full_name = forms.CharField(
        label='Full name',
        widget=forms.TextInput(
            attrs={
                'class': 'Input',
                'placeholder': 'Full name',
            }
        ),
    )

    phone_number = forms.CharField(
        label='Phone number',
        widget=forms.TextInput(
            attrs={
                'class': 'Input',
                'placeholder': 'Phone number',
            }
        ),
    )

    city = forms.CharField(
        label='City',
        widget=forms.TextInput(
            attrs={
                'class': 'Input',
                'placeholder': 'City',
            }
        ),
    )

    address = forms.CharField(
        label='Address',
        widget=forms.TextInput(
            attrs={
                'class': 'Input',
                'placeholder': 'Address',
            }
        ),
    )

    payment_type = forms.ChoiceField(
        label='Payment method',
        choices=PAYMENT_CHOICES,
        widget=forms.Select(
            attrs={
                'class': 'Input',
            }
        ),
    )


