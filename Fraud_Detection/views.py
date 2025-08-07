from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, FileResponse
import pandas as pd
import matplotlib.pyplot as plt
import os
from django.conf import settings
from .ml_model import predict_fraud
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from .models import Prediction  # Import the Prediction model

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('upload')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

def login(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('upload')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

def logout(request):
    auth_logout(request)
    return redirect('login')


@login_required
def upload(request):
    if request.method == 'POST':
        uploaded_file = request.FILES['file']
        df = pd.read_excel(uploaded_file)
        df['Fraud_Prediction'] = predict_fraud(df)

        results = df.to_dict(orient='records')
        # Save prediction to the database

        counts = df['Fraud_Prediction'].value_counts()
        labels = counts.index
        values = counts.values
        colors = ['red', 'green'] if 'Fraudulent' in labels[0] else ['green', 'red']
        explode = (0.1, 0) if len(labels) == 2 else (0,) * len(labels)
        plt.figure(figsize=(8, 6))
        plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors, explode=explode)
        plt.title('Fraudulent vs Not Fraudulent Transactions')
        plt.axis('equal')
        graph_filename = f'fraud_prediction_pie_chart_{request.user.id}_{Prediction.objects.count()}.png' # unique name for graph
        graph_path = os.path.join(settings.MEDIA_ROOT, graph_filename)
        plt.savefig(graph_path)
        plt.close()
        prediction = Prediction.objects.create(user=request.user, prediction_data=results, graph_file_name = graph_filename if graph_filename else '')  # Save to database
        return render(request, 'upload/results.html', {'results': results})  # Remove session storage
    return render(request, 'upload/upload.html')


@login_required
def download_excel(request):
        # Get the latest predictions from the database, for specific user.
        latest_prediction = Prediction.objects.filter(user=request.user).order_by('-created_at').first()
        if not latest_prediction:
                return HttpResponse("No data available for download", status=400)
        results = latest_prediction.prediction_data
        df = pd.DataFrame(results)
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="fraud_detection_results.xlsx"'
        df.to_excel(response, index=False)
        return response

@login_required
def view_graph(request):
    # Get the latest predictions from the database, for specific user
    latest_prediction = Prediction.objects.filter(user=request.user).order_by('-created_at').first()
    if not latest_prediction:
         return HttpResponse("No data available to generate a graph", status=400)

    results = latest_prediction.prediction_data
    graph_filename = latest_prediction.graph_file_name
    if not graph_filename:
            return HttpResponse("Graph file not found", status=404)
    graph_url = os.path.join(settings.MEDIA_URL, graph_filename)


    return render(request, 'upload/graph.html', {'graph_url': graph_url})


@login_required
def download_graph(request):
    latest_prediction = Prediction.objects.filter(user=request.user).order_by('-created_at').first()
    if not latest_prediction:
        return HttpResponse("Graph file not found", status=404)

    graph_filename = latest_prediction.graph_file_name

    if not graph_filename:
            return HttpResponse("Graph file not found", status=404)

    graph_path = os.path.join(settings.MEDIA_ROOT, graph_filename)
    if not os.path.exists(graph_path):
        return HttpResponse("Graph file not found", status=404)
    return FileResponse(open(graph_path, 'rb'), as_attachment=True, filename=graph_filename)

@login_required
def history(request):
    """View to display prediction history for the logged-in user."""
    predictions = Prediction.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'upload/history.html', {'predictions': predictions})

@login_required
def download_excel_prediction(request, prediction_id):
    """Download excel for specific prediction"""
    try:
         prediction = Prediction.objects.get(pk=prediction_id, user=request.user)
    except Prediction.DoesNotExist:
        return HttpResponse("Prediction not found", status=404)
    results = prediction.prediction_data
    df = pd.DataFrame(results)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="prediction_{prediction_id}_results.xlsx"'
    df.to_excel(response, index=False)
    return response


@login_required
def view_graph_prediction(request, prediction_id):
    """View graph for specific prediction"""
    try:
        prediction = Prediction.objects.get(pk=prediction_id, user=request.user)
    except Prediction.DoesNotExist:
        return HttpResponse("Prediction not found", status=404)

    graph_filename = prediction.graph_file_name
    if not graph_filename:
           return HttpResponse("Graph file not found", status=404)

    graph_url = os.path.join(settings.MEDIA_URL, graph_filename)

    return render(request, 'upload/graph_history.html', {'graph_url': graph_url, 'prediction':prediction})

@login_required
def download_graph_prediction(request, prediction_id):
        """Download graph for specific prediction"""
        try:
           prediction = Prediction.objects.get(pk=prediction_id, user=request.user)
        except Prediction.DoesNotExist:
            return HttpResponse("Graph file not found", status=404)

        graph_filename = prediction.graph_file_name
        if not graph_filename:
             return HttpResponse("Graph file not found", status=404)

        graph_path = os.path.join(settings.MEDIA_ROOT, graph_filename)

        if not os.path.exists(graph_path):
                return HttpResponse("Graph file not found", status=404)

        return FileResponse(open(graph_path, 'rb'), as_attachment=True, filename=graph_filename)


@login_required
def delete_prediction(request, prediction_id):
    """Delete a specific prediction."""
    prediction = get_object_or_404(Prediction, pk=prediction_id, user=request.user)
    
     # Delete the graph file associated with this prediction
    if prediction.graph_file_name:
            graph_path = os.path.join(settings.MEDIA_ROOT, prediction.graph_file_name)
            if os.path.exists(graph_path):
                os.remove(graph_path)
    prediction.delete()
    return redirect('history')